"""Every organization role may list folders; only non-viewers change them.

The folder routes used to require `manage-folder` for every method, which
viewers do not have, so `GET /folder` answered 401 to them and the Content
page, the move dialog and the dataset picker had no folders for a viewer.
Reading now needs `read-folder`, which every organization role holds.
"""

from collections.abc import Awaitable, Callable
from uuid import UUID

import pytest
from core.db.models.organization import Organization
from core.db.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from tests.authz.route_world import API, give_org_role, sweep_client

ROLES = ("owner", "admin", "editor", "viewer")


@pytest.fixture
async def members(
    db_session: AsyncSession,
    roles: dict[str, UUID],
    make_org: Callable[[], Awaitable[Organization]],
    make_user: Callable[..., Awaitable[User]],
) -> dict[str, UUID]:
    organization = await make_org()
    ids = {}
    for role in ROLES:
        user = await make_user(organization.id)
        await give_org_role(db_session, user.id, roles[f"organization-{role}"])
        ids[role] = user.id
    await db_session.commit()
    return ids


@pytest.mark.asyncio
@pytest.mark.parametrize("role", ROLES)
async def test_every_role_lists_its_folders(
    auth_on: Callable[..., dict[str, str]], members: dict[str, UUID], role: str
) -> None:
    listed = await sweep_client().get(f"{API}/folder", headers=auth_on(members[role]))
    assert listed.status_code == 200, listed.text


@pytest.mark.asyncio
async def test_a_viewer_cannot_create_a_folder(
    auth_on: Callable[..., dict[str, str]], members: dict[str, UUID]
) -> None:
    created = await sweep_client().post(
        f"{API}/folder",
        json={"name": "Not mine to make"},
        headers=auth_on(members["viewer"]),
    )
    assert created.status_code in (401, 403), created.text


@pytest.mark.asyncio
async def test_an_editor_still_creates_folders(
    auth_on: Callable[..., dict[str, str]], members: dict[str, UUID]
) -> None:
    created = await sweep_client().post(
        f"{API}/folder",
        json={"name": "Editor's folder"},
        headers=auth_on(members["editor"]),
    )
    assert created.status_code == 201, created.text
