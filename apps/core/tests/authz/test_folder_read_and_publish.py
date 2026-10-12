"""Reading one folder, and publishing a project, for every caller who may.

`GET /folder/{id}` used to look the folder up by its creator, so an admin of
the organization space (or anyone a folder was shared with) got 404. Publish
copied the map view from the creator's own view of the project and failed
when there was none; unpublishing a project with no public page failed too.
"""

from collections.abc import Awaitable, Callable
from typing import Any
from uuid import UUID

import pytest
from core.db.models._link_model import UserProjectLink
from core.db.models.organization import Organization
from core.db.models.user import User
from goatlib.models.project import DEFAULT_INITIAL_VIEW_STATE
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tests.authz.route_world import API, build_org_world, give_org_role, sweep_client


async def _world_with_admin(
    db_session: AsyncSession,
    roles: dict[str, UUID],
    make_org: Callable[[], Awaitable[Organization]],
    make_user: Callable[..., Awaitable[User]],
    make_folder: Callable[..., Awaitable[Any]],
    make_layer: Callable[..., Awaitable[Any]],
    make_project: Callable[..., Awaitable[Any]],
    *,
    in_organization_space: bool,
) -> dict[str, Any]:
    world = await build_org_world(
        db_session,
        roles,
        make_org,
        make_user,
        make_folder,
        make_layer,
        make_project,
        in_organization_space=in_organization_space,
    )
    admin = await make_user(world["org"].id)
    await give_org_role(db_session, admin.id, roles["organization-admin"])
    await db_session.commit()
    return {**world, "admin": admin.id}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("in_organization_space", "admin_status"),
    [(True, 200), (False, 404)],
    ids=["organization-space", "personal-space"],
)
async def test_a_folder_is_read_by_whoever_may_read_it(
    db_session: AsyncSession,
    roles: dict[str, UUID],
    auth_on: Callable[..., dict[str, str]],
    make_org: Callable[[], Awaitable[Organization]],
    make_user: Callable[..., Awaitable[User]],
    make_folder: Callable[..., Awaitable[Any]],
    make_layer: Callable[..., Awaitable[Any]],
    make_project: Callable[..., Awaitable[Any]],
    in_organization_space: bool,
    admin_status: int,
) -> None:
    world = await _world_with_admin(
        db_session,
        roles,
        make_org,
        make_user,
        make_folder,
        make_layer,
        make_project,
        in_organization_space=in_organization_space,
    )
    folder_id = world["ids"]["folder_id"]
    client = sweep_client()
    url = f"{API}/folder/{folder_id}"

    created = await client.get(url, headers=auth_on(world["owner"]))
    assert created.status_code == 200, created.text
    assert created.json()["id"] == str(folder_id)
    # An admin reads the organization's folders, never a member's personal ones.
    admin = await client.get(url, headers=auth_on(world["admin"]))
    assert admin.status_code == admin_status, admin.text


@pytest.mark.asyncio
async def test_publish_and_unpublish_never_fail_on_missing_state(
    db_session: AsyncSession,
    roles: dict[str, UUID],
    auth_on: Callable[..., dict[str, str]],
    make_org: Callable[[], Awaitable[Organization]],
    make_user: Callable[..., Awaitable[User]],
    make_folder: Callable[..., Awaitable[Any]],
    make_layer: Callable[..., Awaitable[Any]],
    make_project: Callable[..., Awaitable[Any]],
) -> None:
    world = await _world_with_admin(
        db_session,
        roles,
        make_org,
        make_user,
        make_folder,
        make_layer,
        make_project,
        in_organization_space=False,
    )
    project_id = world["ids"]["project_id"]
    # A project nobody holds a view of, like one whose creator was removed.
    links = await db_session.execute(
        select(UserProjectLink).where(UserProjectLink.project_id == project_id)
    )
    for link in links.scalars():
        await db_session.delete(link)
    await db_session.commit()

    client = sweep_client()
    headers = auth_on(world["owner"])
    base = f"{API}/project/{project_id}"

    never_published = await client.delete(f"{base}/unpublish", headers=headers)
    assert never_published.status_code == 200, never_published.text

    published = await client.post(f"{base}/publish", headers=headers)
    assert published.status_code == 200, published.text
    view = published.json()["config"]["project"]["initial_view_state"]
    assert view["latitude"] == DEFAULT_INITIAL_VIEW_STATE["latitude"]

    for _ in range(2):
        unpublished = await client.delete(f"{base}/unpublish", headers=headers)
        assert unpublished.status_code == 200, unpublished.text


@pytest.mark.asyncio
async def test_publish_skips_an_empty_view_for_the_publishers(
    db_session: AsyncSession,
    roles: dict[str, UUID],
    auth_on: Callable[..., dict[str, str]],
    make_org: Callable[[], Awaitable[Organization]],
    make_user: Callable[..., Awaitable[User]],
    make_folder: Callable[..., Awaitable[Any]],
    make_layer: Callable[..., Awaitable[Any]],
    make_project: Callable[..., Awaitable[Any]],
) -> None:
    world = await _world_with_admin(
        db_session,
        roles,
        make_org,
        make_user,
        make_folder,
        make_layer,
        make_project,
        in_organization_space=True,
    )
    project_id = world["ids"]["project_id"]
    links = await db_session.execute(
        select(UserProjectLink).where(UserProjectLink.project_id == project_id)
    )
    for link in links.scalars():
        link.initial_view_state = {}
        db_session.add(link)
    publisher_view = {**DEFAULT_INITIAL_VIEW_STATE, "latitude": 12.5}
    db_session.add(
        UserProjectLink(
            user_id=world["admin"],
            project_id=project_id,
            initial_view_state=publisher_view,
        )
    )
    await db_session.commit()

    published = await sweep_client().post(
        f"{API}/project/{project_id}/publish", headers=auth_on(world["admin"])
    )
    assert published.status_code == 200, published.text
    view = published.json()["config"]["project"]["initial_view_state"]
    assert view["latitude"] == 12.5
