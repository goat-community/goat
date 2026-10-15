"""The database privileges the assistant needs (Plan 4 review: customer.can
runs with the caller's privileges and reads core's tables).

Roles are cluster-wide and the local Postgres is shared by every checkout, so
the tests that create one run only with ASSISTANT_TEST_ROLES=1 (CI's Postgres is
throwaway and sets it); the test database user must then be a superuser (on
PostgreSQL 16 and later CREATEROLE is not enough to SET ROLE to the new role). The test against a predefined role creates nothing and always runs
where the user may SET ROLE to it."""

import logging
import os
import re
from collections.abc import AsyncIterator
from pathlib import Path

import asyncpg
import pytest
import pytest_asyncio

from assistant import app as app_module
from assistant.config import AssistantSettings
from assistant.db import Database
from assistant.dbcheck import AUTHZ_FUNCTIONS, CUSTOMER_READS, missing_privileges

ROOT = Path(__file__).resolve().parents[3]
AUTHZ_SQL = (
    ROOT / "apps" / "core" / "src" / "core" / "db" / "sql" / "functions" / "authz"
)
GRANTS = ROOT / "apps" / "assistant" / "sql" / "grants.sql"
SRC = ROOT / "apps" / "assistant" / "src" / "assistant"


def test_the_check_covers_every_table_the_authz_functions_read() -> None:
    sql = "\n".join(path.read_text() for path in sorted(AUTHZ_SQL.glob("*.sql")))
    names = {m.strip('"') for m in re.findall(r'customer\.("?[a-z_]+"?)', sql)}
    defined = set(re.findall(r"FUNCTION customer\.([a-z_]+)", sql))
    # Every function the authz files define is one the check looks for ...
    assert defined <= set(AUTHZ_FUNCTIONS), sorted(defined - set(AUTHZ_FUNCTIONS))
    # ... and every other name they use is a table the check (and grants.sql) covers.
    tables = names - defined
    assert tables <= set(CUSTOMER_READS), sorted(tables - set(CUSTOMER_READS))


def test_the_check_covers_the_services_own_reads() -> None:
    own = set()
    for path in SRC.rglob("*.py"):
        own |= set(
            re.findall(r"\.customer\(\s*[\"']([a-z_]+)[\"']\s*\)", path.read_text())
        )
    assert own, "expected Database.customer(...) lookups in the service"
    # Tables need SELECT (CUSTOMER_READS), functions EXECUTE (AUTHZ_FUNCTIONS).
    known = set(CUSTOMER_READS) | set(AUTHZ_FUNCTIONS)
    assert own <= known, sorted(own - known)


def test_grants_file_lists_exactly_the_checked_tables() -> None:
    text = GRANTS.read_text()
    block = re.search(r"GRANT SELECT ON\s+(.*?)\s+TO goat_assistant;", text, re.S)
    assert block, "grants.sql must have one GRANT SELECT ON customer.* block"
    granted = {
        name.strip().removeprefix("customer.").strip('"')
        for name in block.group(1).split(",")
    }
    assert granted == set(CUSTOMER_READS)
    assert (
        "GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA customer TO goat_assistant;" in text
    )
    assert (
        "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA assistant TO goat_assistant;"
        in text
    )


@pytest_asyncio.fixture
async def conn(db: Database) -> AsyncIterator[asyncpg.Connection]:
    async with db.pool.acquire() as connection:
        yield connection


async def test_owner_has_every_privilege_on_the_assistant_tables(
    conn: asyncpg.Connection, settings: AssistantSettings
) -> None:
    missing = await missing_privileges(
        conn, schema=settings.db_schema, customer_schema=settings.customer_schema
    )
    # The test schema has the assistant tables but only a few of core's
    # tables and no authz functions: those are reported as not migrated.
    assert not [
        item
        for item in missing
        if item.startswith(
            ("SELECT ON", "INSERT ON", "UPDATE ON", "DELETE ON", "USAGE ON")
        )
    ]
    assert (
        f'table "{settings.customer_schema}"."folder" (run core\'s migration)'
        in missing
    )
    assert (
        f'function "{settings.customer_schema}".effective_role (run core\'s initial_data)'
        in missing
    )


async def test_a_role_without_schema_usage_is_reported_not_raised(
    conn: asyncpg.Connection, settings: AssistantSettings
) -> None:
    # pg_monitor is a predefined role with no USAGE on the test schema. A lookup
    # by name would raise "permission denied for schema" for it.
    transaction = conn.transaction()
    await transaction.start()
    try:
        try:
            await conn.execute("SET LOCAL ROLE pg_monitor")
        except asyncpg.InsufficientPrivilegeError:
            pytest.skip("the test database user cannot SET ROLE pg_monitor")
        missing = await missing_privileges(
            conn, schema=settings.db_schema, customer_schema=settings.customer_schema
        )
    finally:
        await transaction.rollback()
    assert f'USAGE ON SCHEMA "{settings.db_schema}"' in missing
    assert f'USAGE ON SCHEMA "{settings.customer_schema}"' in missing
    # The object checks of a schema without USAGE are skipped.
    assert not [item for item in missing if 'ON "' in item and "SCHEMA" not in item]


needs_roles = pytest.mark.skipif(
    os.environ.get("ASSISTANT_TEST_ROLES") != "1",
    reason="creates a cluster-wide role; set ASSISTANT_TEST_ROLES=1 on a throwaway Postgres",
)


async def _with_role(
    conn: asyncpg.Connection, settings: AssistantSettings, role: str, *grants: str
) -> list[str]:
    await conn.execute(f'DROP ROLE IF EXISTS "{role}"')
    await conn.execute(f'CREATE ROLE "{role}" NOLOGIN')
    try:
        for grant in grants:
            await conn.execute(grant.format(role=f'"{role}"'))
        async with conn.transaction():
            await conn.execute(f'SET LOCAL ROLE "{role}"')
            return await missing_privileges(
                conn,
                schema=settings.db_schema,
                customer_schema=settings.customer_schema,
            )
    finally:
        # Only when the role exists, so a failed CREATE is not masked.
        if await conn.fetchval("SELECT 1 FROM pg_roles WHERE rolname = $1", role):
            await conn.execute(f'DROP OWNED BY "{role}"')
            await conn.execute(f'DROP ROLE IF EXISTS "{role}"')


@needs_roles
async def test_a_role_without_grants_is_told_what_it_lacks(
    conn: asyncpg.Connection, settings: AssistantSettings
) -> None:
    missing = await _with_role(
        conn, settings, f"assistant_dbcheck_nogrants_{os.getpid()}"
    )
    assert f'USAGE ON SCHEMA "{settings.db_schema}"' in missing


@needs_roles
async def test_a_role_with_usage_only_is_told_which_tables_it_lacks(
    conn: asyncpg.Connection, settings: AssistantSettings
) -> None:
    missing = await _with_role(
        conn,
        settings,
        f"assistant_dbcheck_usage_{os.getpid()}",
        f'GRANT USAGE ON SCHEMA "{settings.db_schema}" TO {{role}}',
    )
    assert f'SELECT ON "{settings.db_schema}"."conversation"' in missing
    assert f'USAGE ON SCHEMA "{settings.db_schema}"' not in missing


async def test_start_logs_what_is_missing_and_never_aborts(
    db: Database,
    settings: AssistantSettings,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    async def lacking(*args: object, **kwargs: object) -> list[str]:
        return ['SELECT ON "customer"."folder"']

    monkeypatch.setattr(app_module, "missing_privileges", lacking)
    with caplog.at_level(logging.ERROR, logger="assistant.app"):
        await app_module._log_missing_privileges(db, settings)
    assert 'SELECT ON "customer"."folder"' in caplog.text
    assert "grants.sql" in caplog.text


async def test_a_failing_check_is_logged_not_raised(
    db: Database,
    settings: AssistantSettings,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    async def explode(*args: object, **kwargs: object) -> list[str]:
        raise RuntimeError("catalog unreadable")

    monkeypatch.setattr(app_module, "missing_privileges", explode)
    with caplog.at_level(logging.ERROR, logger="assistant.app"):
        await app_module._log_missing_privileges(db, settings)
    assert "Checking the database privileges failed" in caplog.text
