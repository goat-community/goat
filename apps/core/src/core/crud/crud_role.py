from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession

from core.crud.base import CRUDBase
from core.db.models import Role
from core.db.models._link_model import UserRoleLink
from core.db.models.organization import OrganizationRolesEnum


class CRUDRole(CRUDBase[Role, Role, Role]):
    async def remove_organization_roles(
        self, db: AsyncSession | AsyncConnection, user_id: UUID | str
    ) -> None:
        """Drop every organization role the user holds.

        Roles are not tied to an organization, so one held from elsewhere
        would count in whichever organization the user is in. Takes a
        connection too, to run inside `session_manager.transaction()`.
        """
        await db.execute(
            delete(UserRoleLink).where(
                UserRoleLink.user_id == user_id,
                UserRoleLink.role_id.in_(
                    select(Role.id).where(
                        Role.name.in_([r.value for r in OrganizationRolesEnum])
                    )
                ),
            )
        )


role = CRUDRole(Role)
