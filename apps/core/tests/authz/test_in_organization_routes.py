"""Inside one organization, members get no more than their role allows.

The same route sweep as test_cross_organization_routes.py, with callers from
the resources' own organization:

- content in a member's personal space is refused to everyone else in the
  organization, admins included;
- content in the organization's shared space (default role viewer) can be
  read by members but not changed, shared, restricted or deleted by viewers
  or editors;
- organization settings, members, invitations, domains, analytics and the
  space's default role are changed by admins only.

Every check here expects a refusal, and a refused request changes nothing,
so one set of resources per scenario serves all routes.
"""

from collections.abc import Awaitable, Callable
from typing import Any
from uuid import UUID

import pytest
from core.db.models.organization import Organization
from core.db.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from tests.authz.route_world import (
    API,
    body,
    build_org_world,
    fill,
    give_org_role,
    sweep_client,
)
from tests.unit.test_route_authorization_inventory import ANONYMOUS, ROUTES

CONTENT = (
    "asset",
    "bundle",
    "content",
    "folder",
    "layer",
    "project",
    "share",
    "template",
)
ORGANIZATION = ("organizations", "space")

# Routes these rules do not apply to. (method, pattern) -> reason.
EXEMPT: dict[tuple[str, str], str] = {
    (
        "POST",
        "template/{template_id}/use",
    ): "creates the caller's own project from a template they can read",
}


def _routes(prefixes: tuple[str, ...], *, writes_only: bool) -> list[tuple[str, str]]:
    return [
        (method, pattern)
        for method, pattern, _ in ROUTES
        if "{" in pattern
        and pattern.split("/")[0] in prefixes
        and (method, pattern) not in ANONYMOUS
        and (method, pattern) not in EXEMPT
        and not (writes_only and method == "GET")
    ]


async def _members(
    db_session: AsyncSession,
    roles: dict[str, UUID],
    make_user: Callable[..., Awaitable[User]],
    org: Organization,
    *role_names: str,
) -> dict[str, UUID]:
    members = {}
    for name in role_names:
        user = await make_user(org.id)
        await give_org_role(db_session, user.id, roles[f"organization-{name}"])
        members[name] = user.id
    await db_session.commit()
    return members


async def _accepted(
    auth_on: Callable[..., dict[str, str]],
    world: dict[str, Any],
    callers: dict[str, UUID],
    routes: list[tuple[str, str]],
) -> list[str]:
    """Every (route, caller) the app did not refuse."""
    client, ids, org = sweep_client(), world["ids"], world["org"].id
    accepted = []
    for method, pattern in routes:
        for who, user_id in callers.items():
            response = await client.request(
                method,
                f"{API}/{fill(pattern, ids)}",
                headers=auth_on(user_id),
                json=body(method, pattern, ids, org) if method != "GET" else None,
            )
            if response.status_code not in (401, 403, 404):
                accepted.append(f"{response.status_code} {method} {pattern} ({who})")
    return accepted


@pytest.mark.asyncio
async def test_personal_content_is_refused_to_the_rest_of_the_organization(
    db_session: AsyncSession,
    roles: dict[str, UUID],
    auth_on: Callable[..., dict[str, str]],
    make_org: Callable[[], Awaitable[Organization]],
    make_user: Callable[..., Awaitable[User]],
    make_folder: Callable[..., Awaitable[Any]],
    make_layer: Callable[..., Awaitable[Any]],
    make_project: Callable[..., Awaitable[Any]],
) -> None:
    world = await build_org_world(
        db_session, roles, make_org, make_user, make_folder, make_layer, make_project
    )
    callers = await _members(
        db_session, roles, make_user, world["org"], "viewer", "editor", "admin"
    )
    routes = _routes(CONTENT, writes_only=False)
    accepted = await _accepted(auth_on, world, callers, routes)
    assert accepted == [], "\n" + "\n".join(accepted)


@pytest.mark.asyncio
async def test_members_cannot_change_shared_content(
    db_session: AsyncSession,
    roles: dict[str, UUID],
    auth_on: Callable[..., dict[str, str]],
    make_org: Callable[[], Awaitable[Organization]],
    make_user: Callable[..., Awaitable[User]],
    make_folder: Callable[..., Awaitable[Any]],
    make_layer: Callable[..., Awaitable[Any]],
    make_project: Callable[..., Awaitable[Any]],
) -> None:
    world = await build_org_world(
        db_session,
        roles,
        make_org,
        make_user,
        make_folder,
        make_layer,
        make_project,
        in_organization_space=True,
    )
    callers = await _members(
        db_session, roles, make_user, world["org"], "viewer", "editor"
    )
    routes = _routes(CONTENT, writes_only=True)
    accepted = await _accepted(auth_on, world, callers, routes)
    assert accepted == [], "\n" + "\n".join(accepted)


@pytest.mark.asyncio
async def test_only_admins_change_the_organization(
    db_session: AsyncSession,
    roles: dict[str, UUID],
    auth_on: Callable[..., dict[str, str]],
    make_org: Callable[[], Awaitable[Organization]],
    make_user: Callable[..., Awaitable[User]],
    make_folder: Callable[..., Awaitable[Any]],
    make_layer: Callable[..., Awaitable[Any]],
    make_project: Callable[..., Awaitable[Any]],
) -> None:
    world = await build_org_world(
        db_session, roles, make_org, make_user, make_folder, make_layer, make_project
    )
    callers = await _members(
        db_session, roles, make_user, world["org"], "viewer", "editor"
    )
    routes = _routes(ORGANIZATION, writes_only=True)
    accepted = await _accepted(auth_on, world, callers, routes)
    assert accepted == [], "\n" + "\n".join(accepted)
