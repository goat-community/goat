"""The processes access check, run against the real authorization functions.

processes asks one question before it runs anything: which of the layers,
projects, folders and bundles a request names may this caller not use?
`processes.services.access_sql` holds that statement; this runs it here,
where `customer.can` and the published-project table exist.
"""

import json
from collections.abc import Awaitable, Callable
from typing import Any
from uuid import UUID, uuid4

import asyncpg
import pytest
from core.core.config import settings
from core.db.models.organization import Organization
from core.db.models.user import User
from processes.services.access_sql import access_check_sql
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from tests.authz.route_world import build_org_world, give_org_role

S = settings.SCHEMA


async def _denied(
    user_id: UUID | None, refs: list[dict[str, Any]]
) -> set[tuple[str, str, str]]:
    dsn = str(settings.ASYNC_SQLALCHEMY_DATABASE_URI).replace("+psycopg", "")
    connection = await asyncpg.connect(dsn)
    try:
        rows = await connection.fetch(
            access_check_sql(S), str(user_id) if user_id else None, json.dumps(refs)
        )
    finally:
        await connection.close()
    return {(row["kind"], row["raw_id"], row["action"]) for row in rows}


def _ref(kind: str, value: Any, action: str = "read") -> dict[str, Any]:
    return {"kind": kind, "id": str(value), "action": action}


@pytest.fixture
async def world(
    db_session: AsyncSession,
    roles: dict[str, UUID],
    authz_sql: None,
    make_org: Callable[[], Awaitable[Organization]],
    make_user: Callable[..., Awaitable[User]],
    make_folder: Callable[..., Awaitable[Any]],
    make_layer: Callable[..., Awaitable[Any]],
    make_project: Callable[..., Awaitable[Any]],
) -> dict[str, Any]:
    world = await build_org_world(
        db_session, roles, make_org, make_user, make_folder, make_layer, make_project
    )
    colleague = await make_user(world["org"].id)
    await give_org_role(db_session, colleague.id, roles["organization-viewer"])
    other_org = await make_org()
    outsider = await make_user(other_org.id)
    await give_org_role(db_session, outsider.id, roles["organization-admin"])
    await db_session.commit()
    return {**world, "colleague": colleague.id, "outsider": outsider.id}


@pytest.mark.asyncio
async def test_the_owner_may_use_their_own_resources(world: dict[str, Any]) -> None:
    ids = world["ids"]
    refs = [
        _ref("layer", ids["layer_id"]),
        _ref("layer_project", ids["layer_project_id"]),
        _ref("project", ids["project_id"], "write"),
        _ref("folder", ids["folder_id"], "write"),
        _ref("bundle", ids["bundle_id"]),
    ]
    assert await _denied(world["owner"], refs) == set()


@pytest.mark.asyncio
async def test_others_may_not_use_private_resources(world: dict[str, Any]) -> None:
    ids = world["ids"]
    refs = [
        _ref("layer", ids["layer_id"]),
        _ref("layer_project", ids["layer_project_id"]),
        _ref("project", ids["project_id"], "write"),
        _ref("folder", ids["folder_id"], "write"),
        _ref("bundle", ids["bundle_id"]),
    ]
    expected = {(r["kind"], r["id"], r["action"]) for r in refs}
    for caller in (world["colleague"], world["outsider"], None):
        assert await _denied(caller, refs) == expected, caller


@pytest.mark.asyncio
async def test_a_published_layer_is_readable_by_anyone(
    db_session: AsyncSession, world: dict[str, Any]
) -> None:
    ids = world["ids"]
    await db_session.execute(
        text(
            f"INSERT INTO {S}.project_public (project_id, config, updated_at) "
            "VALUES (:p, CAST(:c AS jsonb), now())"
        ),
        {
            "p": ids["project_id"],
            "c": json.dumps({"layers": [{"layer_id": str(ids["layer_id"])}]}),
        },
    )
    await db_session.commit()
    layer = _ref("layer", ids["layer_id"])
    assert await _denied(None, [layer]) == set()
    # Publishing reads, it does not hand out writes.
    project = _ref("project", ids["project_id"], "write")
    assert await _denied(world["outsider"], [project]) == {
        ("project", str(ids["project_id"]), "write")
    }


@pytest.mark.asyncio
async def test_a_public_dataset_is_readable_by_every_signed_in_user(
    db_session: AsyncSession, world: dict[str, Any]
) -> None:
    """`public_read` opens a layer to signed-in users of any organization,
    not to anonymous callers."""
    ids = world["ids"]
    await db_session.execute(
        text(f"UPDATE {S}.layer SET public_read = TRUE WHERE id = :l"),
        {"l": ids["layer_id"]},
    )
    await db_session.commit()
    layer = _ref("layer", ids["layer_id"])
    assert await _denied(world["outsider"], [layer]) == set()
    assert await _denied(None, [layer]) == {("layer", str(ids["layer_id"]), "read")}


@pytest.mark.asyncio
async def test_a_catalog_dataset_is_readable_by_anyone(
    db_session: AsyncSession, world: dict[str, Any]
) -> None:
    ids = world["ids"]
    await db_session.execute(
        text(f"UPDATE {S}.layer SET catalog_external_uid = :u WHERE id = :l"),
        {"u": f"stac-{uuid4().hex}", "l": ids["layer_id"]},
    )
    await db_session.commit()
    assert await _denied(None, [_ref("layer", ids["layer_id"])]) == set()


@pytest.mark.asyncio
async def test_unknown_and_malformed_ids_are_denied(world: dict[str, Any]) -> None:
    refs = [
        _ref("layer", uuid4()),
        _ref("layer", "/app/data/ducklake/somebody/t_x.parquet"),
        _ref("layer_project", "999999999"),
        _ref("layer_project", "not-a-number"),
        _ref("layer_project", "99999999999999999999"),  # beyond bigint
        _ref("layer", f"{uuid4()}' OR '1'='1"),
        _ref("project", "'; DROP TABLE layer; --", "write"),
    ]
    expected = {(r["kind"], r["id"], r["action"]) for r in refs}
    assert await _denied(world["owner"], refs) == expected


@pytest.mark.asyncio
async def test_an_editor_of_a_shared_project_writes_results_into_its_folder(
    db_session: AsyncSession,
    roles: dict[str, UUID],
    authz_sql: None,
    make_org: Callable[[], Awaitable[Organization]],
    make_user: Callable[..., Awaitable[User]],
    make_folder: Callable[..., Awaitable[Any]],
    make_project: Callable[..., Awaitable[Any]],
) -> None:
    """A tool run puts its result in the project's folder, which belongs to
    the project's owner. An editor of the project may write there for that
    project, and only for it: not into another of the owner's folders, and
    not when the request names no project or one they cannot edit."""
    org = await make_org()
    owner, editor = await make_user(org.id), await make_user(org.id)
    for user in (owner, editor):
        await give_org_role(db_session, user.id, roles["organization-editor"])
    home = await make_folder(owner)
    other_folder = await make_folder(owner)
    project = await make_project(owner, home)
    unshared = await make_project(owner, home)
    await db_session.execute(
        text(
            f"INSERT INTO {S}.resource_grant "
            "(resource_type, resource_id, grantee_type, grantee_id, role_id, granted_by) "
            "VALUES ('project', :p, 'user', :u, :role, :by)"
        ),
        {
            "p": project.id,
            "u": editor.id,
            "role": roles["project-editor"],
            "by": owner.id,
        },
    )
    await db_session.commit()

    into_project = [
        _ref("project", project.id, "write"),
        _ref("folder", home.id, "write"),
    ]
    assert await _denied(editor.id, into_project) == set()

    elsewhere = [
        _ref("project", project.id, "write"),
        _ref("folder", other_folder.id, "write"),
    ]
    assert await _denied(editor.id, elsewhere) == {
        ("folder", str(other_folder.id), "write")
    }

    assert await _denied(editor.id, [_ref("folder", home.id, "write")]) == {
        ("folder", str(home.id), "write")
    }

    not_editable = [
        _ref("project", unshared.id, "write"),
        _ref("folder", home.id, "write"),
    ]
    assert await _denied(editor.id, not_editable) == {
        ("project", str(unshared.id), "write"),
        ("folder", str(home.id), "write"),
    }
