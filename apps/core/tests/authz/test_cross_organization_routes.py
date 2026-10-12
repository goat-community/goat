"""No route lets one organization reach another organization's resources.

Organization A gets one resource of every kind a route can name; an admin of
organization B then calls every route that takes an id, with A's ids, through
the real authorization (``auth_on``). Each answer must be a refusal (401, 403
or 404). The routes come from the app itself, so a new route is covered as
soon as it exists, and a route whose path has a placeholder this file does
not know fails the test instead of being skipped.

A 422 proves nothing (the request was rejected before any access decision),
so routes answering 422 are listed too until `route_world.body` gives them
a valid body.
"""

from collections.abc import Awaitable, Callable
from typing import Any
from uuid import UUID

import pytest
from core.core.config import settings
from core.db.models.organization import Organization
from core.db.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from tests.authz.route_world import (
    body,
    build_org_world,
    fill,
    give_org_role,
    sweep_client,
)
from tests.unit.test_route_authorization_inventory import ANONYMOUS, ROUTES

S = settings.SCHEMA
API = settings.API_V2_STR

# Routes where a placeholder names the caller's own data, not A's: there is
# nothing of A's to reach. (method, pattern) -> reason.
NOT_CROSS_ORGANIZATION: dict[tuple[str, str], str] = {
    (
        "PUT",
        "favorite/{item_type}/{item_id}",
    ): "adds an id to the caller's own favourites list",
    (
        "DELETE",
        "favorite/{item_type}/{item_id}",
    ): "removes an id from the caller's own list",
}


@pytest.fixture
async def world(
    db_session: AsyncSession,
    roles: dict[str, UUID],
    make_org: Callable[[], Awaitable[Organization]],
    make_user: Callable[..., Awaitable[User]],
    make_folder: Callable[..., Awaitable[Any]],
    make_layer: Callable[..., Awaitable[Any]],
    make_project: Callable[..., Awaitable[Any]],
) -> dict[str, Any]:
    """Organization A's resources; B's admin and an org-less user as callers."""
    world = await build_org_world(
        db_session,
        roles,
        make_org,
        make_user,
        make_folder,
        make_layer,
        make_project,
        owner_role="organization-owner",
    )
    org_b = await make_org()
    b_admin = await make_user(org_b.id)
    await give_org_role(db_session, b_admin.id, roles["organization-admin"])
    # A signed-in user in no organization: what anyone has after signing up.
    loner = await make_user(None)
    await db_session.commit()
    return {**world, "caller": b_admin.id, "caller_org": org_b.id, "loner": loner.id}


def _cross_organization_routes() -> list[tuple[str, str]]:
    return [
        (method, pattern)
        for method, pattern, _ in ROUTES
        if "{" in pattern
        and (method, pattern) not in ANONYMOUS
        and (method, pattern) not in NOT_CROSS_ORGANIZATION
    ]


@pytest.mark.asyncio
async def test_no_route_reaches_another_organizations_resources(
    auth_on: Callable[..., dict[str, str]],
    world: dict[str, Any],
) -> None:
    ids = world["ids"]
    callers = {
        "admin of another organization": auth_on(world["caller"]),
        "user in no organization": auth_on(world["loner"]),
        "no token": {},
    }
    client = sweep_client()
    leaks, unproven, errors = [], [], []
    for (method, pattern), (who, headers) in (
        (route, caller)
        for route in _cross_organization_routes()
        for caller in callers.items()
    ):
        path = fill(pattern, ids)
        response = await client.request(
            method,
            f"{API}/{path}",
            headers=headers,
            json=body(method, pattern, ids, world["caller_org"])
            if method != "GET"
            else None,
        )
        line = f"{response.status_code} {method} {pattern} ({who})"
        if response.status_code in (401, 403, 404):
            continue
        if response.status_code == 422:
            unproven.append(line)
        elif response.status_code >= 500:
            errors.append(line)
        else:
            leaks.append(f"{line}: {response.text[:120]}")

    report = "\n".join(
        [f"LEAK  {x}" for x in leaks]
        + [f"ERROR {x}" for x in errors]
        + [f"422   {x}" for x in unproven]
    )
    assert not (leaks or errors or unproven), "\n" + report
