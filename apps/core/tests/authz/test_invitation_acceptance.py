"""Accepting an organization invitation never carries roles across organizations.

A user belongs to one organization, and roles are not tied to one: an owner
role held in the user's own organization would make them owner of any
organization they join. Creating an invitation already refuses a user who
has an organization; accepting refuses it too, so an invitation sent before
the invitee set up an organization of their own cannot be used to join with
that owner role. A user who joins holds only the role they were invited with.
"""

from collections.abc import Awaitable, Callable
from uuid import UUID

import pytest
from core.core.config import settings
from core.db.models.invitation import (
    Invitation,
    InvitationStatusEnum,
    InvitationType,
)
from core.db.models.organization import Organization
from core.db.models.user import User
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from tests.authz.route_world import API, give_org_role, sweep_client

S = settings.SCHEMA


async def _invite(
    db: AsyncSession,
    organization_id: UUID,
    sent_by: UUID,
    invitee_id: UUID,
    role: str = "organization-editor",
) -> UUID:
    """A pending invitation to join with `role`, addressed to the email the
    invitee's test token carries."""
    invitation = Invitation(
        send_by=sent_by,
        organization_id=organization_id,
        type=InvitationType.organization,
        payload={
            "organization_id": str(organization_id),
            "role": role,
            "user_email": f"{str(invitee_id)[:8]}@goat.test",
        },
        status=InvitationStatusEnum.pending,
    )
    db.add(invitation)
    await db.flush()
    return invitation.id


async def _roles_of(db: AsyncSession, user_id: UUID) -> set[str]:
    rows = await db.execute(
        text(
            f"SELECT r.name FROM {S}.user_role ur JOIN {S}.role r ON r.id = ur.role_id "
            "WHERE ur.user_id = :u"
        ),
        {"u": user_id},
    )
    return {row[0] for row in rows}


async def _organization_of(db: AsyncSession, user_id: UUID) -> UUID | None:
    return (
        await db.execute(
            text(f"SELECT organization_id FROM {S}.user WHERE id = :id"),
            {"id": user_id},
        )
    ).scalar_one()


async def _status_of(db: AsyncSession, invitation_id: UUID) -> str:
    return (
        await db.execute(
            text(f"SELECT status FROM {S}.invitation WHERE id = :id"),
            {"id": invitation_id},
        )
    ).scalar_one()


@pytest.mark.asyncio
async def test_a_member_of_another_organization_cannot_accept(
    db_session: AsyncSession,
    auth_on: Callable[..., dict[str, str]],
    roles: dict[str, UUID],
    make_org: Callable[[], Awaitable[Organization]],
    make_user: Callable[..., Awaitable[User]],
) -> None:
    inviting_org_id, own_org_id = (await make_org()).id, (await make_org()).id
    inviter_id = (await make_user(inviting_org_id)).id
    await give_org_role(db_session, inviter_id, roles["organization-owner"])
    invitee_id = (await make_user(None)).id
    invitation_id = await _invite(db_session, inviting_org_id, inviter_id, invitee_id)
    # The invitee then sets up an organization of their own, as its owner.
    await db_session.execute(
        text(f"UPDATE {S}.user SET organization_id = :o WHERE id = :u"),
        {"o": own_org_id, "u": invitee_id},
    )
    await give_org_role(db_session, invitee_id, roles["organization-owner"])
    await db_session.commit()

    accepted = await sweep_client().patch(
        f"{API}/users/invitations/{invitation_id}", headers=auth_on(invitee_id)
    )

    assert accepted.status_code == 400, accepted.text
    db_session.expire_all()
    assert await _organization_of(db_session, invitee_id) == own_org_id
    assert await _roles_of(db_session, invitee_id) == {"organization-owner"}
    assert await _status_of(db_session, invitation_id) == "pending"


@pytest.mark.asyncio
async def test_a_user_joins_with_only_the_invited_role(
    db_session: AsyncSession,
    auth_on: Callable[..., dict[str, str]],
    roles: dict[str, UUID],
    make_org: Callable[[], Awaitable[Organization]],
    make_user: Callable[..., Awaitable[User]],
) -> None:
    inviting_org_id = (await make_org()).id
    inviter_id = (await make_user(inviting_org_id)).id
    await give_org_role(db_session, inviter_id, roles["organization-owner"])
    invitee_id = (await make_user(None)).id
    # An organization role left over from before, with no organization behind it.
    await give_org_role(db_session, invitee_id, roles["organization-owner"])
    invitation_id = await _invite(db_session, inviting_org_id, inviter_id, invitee_id)
    await db_session.commit()

    accepted = await sweep_client().patch(
        f"{API}/users/invitations/{invitation_id}", headers=auth_on(invitee_id)
    )

    assert accepted.status_code == 204, accepted.text
    db_session.expire_all()
    assert await _organization_of(db_session, invitee_id) == inviting_org_id
    assert await _roles_of(db_session, invitee_id) == {"organization-editor"}
    assert await _status_of(db_session, invitation_id) == "accepted"


@pytest.mark.asyncio
@pytest.mark.parametrize("broken", ["suspended organization", "unknown role"])
async def test_a_broken_invitation_changes_nothing(
    broken: str,
    db_session: AsyncSession,
    auth_on: Callable[..., dict[str, str]],
    roles: dict[str, UUID],
    make_org: Callable[[], Awaitable[Organization]],
    make_user: Callable[..., Awaitable[User]],
) -> None:
    """Everything is checked before the first write, so a refused invitation
    leaves the user exactly as they were."""
    inviting_org_id = (await make_org()).id
    inviter_id = (await make_user(inviting_org_id)).id
    invitee_id = (await make_user(None)).id
    await give_org_role(db_session, invitee_id, roles["organization-viewer"])
    invitation_id = await _invite(
        db_session,
        inviting_org_id,
        inviter_id,
        invitee_id,
        role="organization-unknown"
        if broken == "unknown role"
        else "organization-editor",
    )
    if broken == "suspended organization":
        await db_session.execute(
            text(f"UPDATE {S}.organization SET suspended = true WHERE id = :o"),
            {"o": inviting_org_id},
        )
    await db_session.commit()

    accepted = await sweep_client().patch(
        f"{API}/users/invitations/{invitation_id}", headers=auth_on(invitee_id)
    )

    assert accepted.status_code == 404, accepted.text
    db_session.expire_all()
    assert await _organization_of(db_session, invitee_id) is None
    assert await _roles_of(db_session, invitee_id) == {"organization-viewer"}
    assert await _status_of(db_session, invitation_id) == "pending"
