"""A team route only passes for a team of the caller's own organization.

The team id is taken from the route pattern (``teams/{team_id}/...``), so the
check covers every team route, seeded or not, including adding and listing
members.
"""

from collections.abc import Awaitable, Callable
from uuid import UUID, uuid4

import pytest
from core.core.config import settings
from core.db.models.organization import Organization
from core.db.models.user import User
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

S = settings.SCHEMA
OTHER_ORG_TEAM = "does not belong to organization from user"


async def _denial(
    db: AsyncSession, user_id: UUID, pattern: str, path: str, method: str
) -> str:
    """Why authorization() refused, or "" when it allowed the request."""
    try:
        await db.execute(
            text(f"SELECT {S}.authorization(:u, :res, :path, :m)"),
            {"u": user_id, "res": pattern, "path": path, "m": method},
        )
    except DBAPIError as error:
        await db.rollback()
        return str(error.orig)
    return ""


async def _user_with_role(
    db: AsyncSession,
    make_user: Callable[..., Awaitable[User]],
    org: Organization,
    role_id: UUID,
) -> UUID:
    user = await make_user(org.id)
    await db.execute(
        text(f"INSERT INTO {S}.user_role (user_id, role_id) VALUES (:u, :r)"),
        {"u": user.id, "r": role_id},
    )
    return user.id


async def _team(db: AsyncSession, org: Organization) -> UUID:
    team_id = uuid4()
    await db.execute(
        text(
            f"INSERT INTO {S}.team (id, name, organization_id) VALUES (:t, 'Team', :o)"
        ),
        {"t": team_id, "o": org.id},
    )
    return team_id


@pytest.mark.asyncio
async def test_team_routes_reject_a_team_of_another_organization(
    db_session: AsyncSession,
    roles: dict[str, UUID],
    make_org: Callable[[], Awaitable[Organization]],
    make_user: Callable[..., Awaitable[User]],
) -> None:
    org, other_org = await make_org(), await make_org()
    team = await _team(db_session, org)
    editor = await _user_with_role(
        db_session, make_user, org, roles["organization-editor"]
    )
    viewer = await _user_with_role(
        db_session, make_user, org, roles["organization-viewer"]
    )
    outside_editor = await _user_with_role(
        db_session, make_user, other_org, roles["organization-editor"]
    )
    outside_viewer = await _user_with_role(
        db_session, make_user, other_org, roles["organization-viewer"]
    )
    await db_session.commit()

    requests = [
        (outside_editor, "teams/{team_id}/profile", f"teams/{team}/profile", "PATCH"),
        (outside_editor, "teams/{team_id}", f"teams/{team}", "DELETE"),
        (outside_viewer, "teams/{team_id}", f"teams/{team}", "GET"),
        (outside_viewer, "teams/{team_id}/members", f"teams/{team}/members", "GET"),
        (
            outside_viewer,
            "teams/{team_id}/users/{user_id}",
            f"teams/{team}/users/{outside_viewer}",
            "POST",
        ),
    ]
    for user_id, pattern, path, method in requests:
        reason = await _denial(db_session, user_id, pattern, path, method)
        assert OTHER_ORG_TEAM in reason, f"{method} {path} let an outsider through"

    # The same requests from inside the organization are unaffected.
    assert (
        await _denial(
            db_session,
            editor,
            "teams/{team_id}/profile",
            f"teams/{team}/profile",
            "PATCH",
        )
        == ""
    )
    assert (
        await _denial(
            db_session,
            editor,
            "teams/{team_id}/members",
            f"teams/{team}/members",
            "GET",
        )
        == ""
    )

    # Adding and removing members has its own resource, so an ordinary member
    # reaches the handler (which lets them leave) instead of needing
    # delete-team.
    assert (
        await _denial(
            db_session,
            viewer,
            "teams/{team_id}/users/{user_id}",
            f"teams/{team}/users/{viewer}",
            "DELETE",
        )
        == ""
    )


@pytest.mark.asyncio
async def test_an_unknown_team_is_refused(
    db_session: AsyncSession,
    roles: dict[str, UUID],
    make_org: Callable[[], Awaitable[Organization]],
    make_user: Callable[..., Awaitable[User]],
) -> None:
    org = await make_org()
    editor = await _user_with_role(
        db_session, make_user, org, roles["organization-editor"]
    )
    await db_session.commit()

    reason = await _denial(
        db_session, editor, "teams/{team_id}", f"teams/{uuid4()}", "DELETE"
    )
    assert OTHER_ORG_TEAM in reason
