"""GOAT-side data the support service needs: users, orgs and read markers."""

from collections.abc import Mapping, Sequence
from typing import Literal, Protocol
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col

from core.db.models._link_model import UserRoleLink
from core.db.models.organization import Organization, OrganizationRolesEnum
from core.db.models.role import Role
from core.db.models.support import SupportTicketRead
from core.db.models.system_setting import SystemSetting
from core.db.models.user import User
from core.support.types import Member, SupportUser

_ADMIN_ROLES = (OrganizationRolesEnum.owner.value, OrganizationRolesEnum.admin.value)
# Ticket id 0 never exists in Odoo: its row records which contact the user's markers
# were seeded for (last_seen_message_id = that contact id; 0 = an unknown contact).
SEED_MARKER = 0


def _full_name(first: str | None, last: str | None, email: str) -> str:
    return " ".join(p for p in (first, last) if p) or email


class SupportStore(Protocol):
    async def load_user(self, user_id: UUID) -> SupportUser: ...
    async def save_contact_id(self, user_id: UUID, contact_id: int) -> None: ...
    async def clear_contact_id(self, user_id: UUID) -> None: ...
    async def org_company_id(self, org_id: UUID) -> int | None: ...
    async def org_members(self, org_id: UUID) -> list[Member]: ...
    async def seeded_contact(self, user_id: UUID) -> int | None: ...
    async def set_seeded_contact(self, user_id: UUID, contact_id: int) -> None: ...
    async def read_markers(
        self, user_id: UUID, ticket_ids: Sequence[int]
    ) -> dict[int, int]: ...
    async def set_read_markers(
        self, user_id: UUID, markers: Mapping[int, int]
    ) -> None: ...


class SqlSupportStore:
    def __init__(self, session: AsyncSession) -> None:
        self._db = session

    async def load_user(self, user_id: UUID) -> SupportUser:
        row = (
            await self._db.execute(
                select(
                    col(User.id),
                    col(User.email),
                    col(User.firstname),
                    col(User.lastname),
                    col(User.organization_id),
                    col(User.odoo_contact_id),
                ).where(col(User.id) == user_id)
            )
        ).one()
        admin = (
            await self._db.execute(
                select(func.count())
                .select_from(UserRoleLink)
                .join(Role, col(Role.id) == col(UserRoleLink.role_id))
                .where(
                    col(UserRoleLink.user_id) == user_id,
                    col(Role.name).in_(_ADMIN_ROLES),
                )
            )
        ).scalar_one() > 0
        lang = (
            await self._db.execute(
                select(col(SystemSetting.preferred_language)).where(
                    col(SystemSetting.user_id) == user_id
                )
            )
        ).scalar_one_or_none()
        lang_value: Literal["en", "de"] = (
            "de" if str(getattr(lang, "value", lang)) == "de" else "en"
        )
        return SupportUser(
            id=row.id,
            email=row.email,
            name=_full_name(row.firstname, row.lastname, row.email),
            lang=lang_value,
            org_id=row.organization_id,
            is_org_admin=admin,
            contact_id=row.odoo_contact_id,
        )

    async def save_contact_id(self, user_id: UUID, contact_id: int) -> None:
        await self._db.execute(
            update(User)
            .where(col(User.id) == user_id)
            .values(odoo_contact_id=contact_id)
        )
        await self._db.commit()

    async def clear_contact_id(self, user_id: UUID) -> None:
        await self._db.execute(
            update(User).where(col(User.id) == user_id).values(odoo_contact_id=None)
        )
        await self._db.commit()

    async def org_company_id(self, org_id: UUID) -> int | None:
        return (
            await self._db.execute(
                select(col(Organization.odoo_company_id)).where(
                    col(Organization.id) == org_id
                )
            )
        ).scalar_one_or_none()

    async def org_members(self, org_id: UUID) -> list[Member]:
        rows = (
            await self._db.execute(
                select(
                    col(User.id),
                    col(User.email),
                    col(User.firstname),
                    col(User.lastname),
                    col(User.odoo_contact_id),
                )
                .where(col(User.organization_id) == org_id)
                .order_by(col(User.firstname), col(User.lastname))
            )
        ).all()
        return [
            Member(
                r.id,
                r.email,
                _full_name(r.firstname, r.lastname, r.email),
                r.odoo_contact_id,
            )
            for r in rows
        ]

    async def seeded_contact(self, user_id: UUID) -> int | None:
        """The contact the read markers were seeded for; None = never seeded."""
        return (
            await self._db.execute(
                select(col(SupportTicketRead.last_seen_message_id)).where(
                    col(SupportTicketRead.user_id) == user_id,
                    col(SupportTicketRead.ticket_id) == SEED_MARKER,
                )
            )
        ).scalar_one_or_none()

    async def set_seeded_contact(self, user_id: UUID, contact_id: int) -> None:
        # Overwritten, not `greatest`: a relink may go to a lower contact id.
        stmt = pg_insert(SupportTicketRead).values(
            user_id=user_id, ticket_id=SEED_MARKER, last_seen_message_id=contact_id
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["user_id", "ticket_id"],
            set_={
                "last_seen_message_id": stmt.excluded.last_seen_message_id,
                "updated_at": func.now(),
            },
        )
        await self._db.execute(stmt)
        await self._db.commit()

    async def read_markers(
        self, user_id: UUID, ticket_ids: Sequence[int]
    ) -> dict[int, int]:
        if not ticket_ids:
            return {}
        rows = (
            await self._db.execute(
                select(
                    col(SupportTicketRead.ticket_id),
                    col(SupportTicketRead.last_seen_message_id),
                ).where(
                    col(SupportTicketRead.user_id) == user_id,
                    col(SupportTicketRead.ticket_id).in_(list(ticket_ids)),
                )
            )
        ).all()
        return {r.ticket_id: r.last_seen_message_id for r in rows}

    async def set_read_markers(self, user_id: UUID, markers: Mapping[int, int]) -> None:
        if not markers:
            return
        stmt = pg_insert(SupportTicketRead).values(
            [
                {"user_id": user_id, "ticket_id": t, "last_seen_message_id": msg}
                for t, msg in markers.items()
            ]
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["user_id", "ticket_id"],
            set_={
                "last_seen_message_id": func.greatest(
                    col(SupportTicketRead.last_seen_message_id),
                    stmt.excluded.last_seen_message_id,
                ),
                "updated_at": func.now(),
            },
        )
        await self._db.execute(stmt)
        await self._db.commit()
