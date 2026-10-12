"""Custom-domain routes are gated to the organization's own admins.

The route layer (``auth_z`` -> ``authorization()``) is what enforces it: the
seeded resources ask for ``update-organization`` to change a domain and
``read-organization`` to list one, and ``check_organization`` rejects a path
naming an organization other than the caller's. That the real routes produce
these patterns is pinned in ``tests/unit/test_organization_route_resources.py``.
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
from tests.authz.conftest import _call, find_resource

S = settings.SCHEMA
DOMAINS = "organizations/{organization_id}/domains"
DOMAIN = "organizations/{organization_id}/domains/{domain_id}"
RECHECK = "organizations/{organization_id}/domains/{domain_id}/recheck"
# check_organization's message for a path naming another organization.
OTHER_ORG = "does not correspond to organization from user"


async def _authorized(
    db: AsyncSession, user_id: UUID, pattern: str, path: str, method: str
) -> bool:
    return await _call(
        db,
        f"SELECT {S}.authorization(:u, :res, :path, :m)",
        {"u": user_id, "res": pattern, "path": path, "m": method},
    )


async def _denial(
    db: AsyncSession, user_id: UUID, pattern: str, path: str, method: str
) -> str:
    """Why authorization() refused, so a test can tell the organization
    check apart from any other failure that would also read as "denied"."""
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
) -> User:
    user = await make_user(org.id)
    await db.execute(
        text(f"INSERT INTO {S}.user_role (user_id, role_id) VALUES (:u, :r)"),
        {"u": user.id, "r": role_id},
    )
    return user


@pytest.mark.asyncio
async def test_only_admins_of_the_organization_change_its_domains(
    db_session: AsyncSession,
    roles: dict[str, UUID],
    make_org: Callable[[], Awaitable[Organization]],
    make_user: Callable[..., Awaitable[User]],
) -> None:
    for pattern, method in (
        (DOMAINS, "GET"),
        (DOMAINS, "POST"),
        (DOMAIN, "DELETE"),
        (RECHECK, "POST"),
    ):
        await find_resource(db_session, pattern, method)

    org = await make_org()
    other_org = await make_org()
    admin = await _user_with_role(
        db_session, make_user, org, roles["organization-admin"]
    )
    owner = await _user_with_role(
        db_session, make_user, org, roles["organization-owner"]
    )
    editor = await _user_with_role(
        db_session, make_user, org, roles["organization-editor"]
    )
    viewer = await _user_with_role(
        db_session, make_user, org, roles["organization-viewer"]
    )
    outside_admin = await _user_with_role(
        db_session, make_user, other_org, roles["organization-admin"]
    )
    await db_session.commit()
    # Plain ids: a denied call rolls the session back, which expires the ORM
    # objects, and reading an attribute afterwards would need a lazy load.
    admin_id, owner_id, editor_id, viewer_id, outside_id = (
        admin.id,
        owner.id,
        editor.id,
        viewer.id,
        outside_admin.id,
    )

    domains = f"organizations/{org.id}/domains"
    domain = f"{domains}/{uuid4()}"
    writes = ((DOMAINS, domains, "POST"), (DOMAIN, domain, "DELETE"))
    writes += ((RECHECK, f"{domain}/recheck", "POST"),)

    for pattern, path, method in writes:
        assert await _authorized(db_session, admin_id, pattern, path, method) is True
        assert await _authorized(db_session, owner_id, pattern, path, method) is True
        assert (
            await _authorized(db_session, editor_id, pattern, path, method) is False
        ), f"an editor must not {method} {pattern}"
        assert await _authorized(db_session, viewer_id, pattern, path, method) is False
        assert OTHER_ORG in await _denial(
            db_session, outside_id, pattern, path, method
        ), f"an admin of another organization must not {method} {pattern}"

    # Members may see which domains their organization has; outsiders may not.
    assert await _authorized(db_session, viewer_id, DOMAINS, domains, "GET") is True
    assert OTHER_ORG in await _denial(db_session, outside_id, DOMAINS, domains, "GET")


@pytest.mark.asyncio
async def test_an_organization_route_rejects_a_path_naming_another_organization(
    db_session: AsyncSession,
    roles: dict[str, UUID],
    make_org: Callable[[], Awaitable[Organization]],
    make_user: Callable[..., Awaitable[User]],
) -> None:
    """The organization-in-path check covers every `organizations/{id}` route,
    not only domains: an admin may rename their own organization only."""
    pattern = "organizations/{organization_id}/profile"
    await find_resource(db_session, pattern, "PATCH")
    org = await make_org()
    other_org = await make_org()
    admin = await _user_with_role(
        db_session, make_user, org, roles["organization-admin"]
    )
    await db_session.commit()
    admin_id, own, other = admin.id, org.id, other_org.id

    assert await _authorized(
        db_session, admin_id, pattern, f"organizations/{own}/profile", "PATCH"
    )
    assert OTHER_ORG in await _denial(
        db_session, admin_id, pattern, f"organizations/{other}/profile", "PATCH"
    )


@pytest.mark.asyncio
async def test_an_owner_cannot_delete_another_organization(
    db_session: AsyncSession,
    roles: dict[str, UUID],
    make_org: Callable[[], Awaitable[Organization]],
    make_user: Callable[..., Awaitable[User]],
) -> None:
    """`DELETE /organizations/{id}` has no check of its own in the handler, so
    the route layer is the only thing keeping an owner to their own org."""
    pattern = "organizations/{organization_id}"
    await find_resource(db_session, pattern, "DELETE")
    org = await make_org()
    other_org = await make_org()
    owner = await _user_with_role(
        db_session, make_user, org, roles["organization-owner"]
    )
    await db_session.commit()
    owner_id, own, other = owner.id, org.id, other_org.id

    assert await _authorized(
        db_session, owner_id, pattern, f"organizations/{own}", "DELETE"
    )
    assert OTHER_ORG in await _denial(
        db_session, owner_id, pattern, f"organizations/{other}", "DELETE"
    )
