"""`layer_serial_counter`: the model, its cascade, and migration 0011 up and down.

Runs against the per-process test schema the root conftest builds with
``create_all`` — so the table is there from the model, exactly as on a fresh
database — and runs the revision's ``upgrade``/``downgrade`` through alembic's
operations on that schema only.
"""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from core.core.config import settings
from core.db.models import LayerSerialCounter
from core.endpoints.deps import session_manager
from sqlalchemy import text

pytestmark = pytest.mark.unit

MIGRATION = (
    Path(__file__).resolve().parents[2]
    / "alembic"
    / "versions"
    / "0011_layer_serial_counter.py"
)


def _load_migration() -> ModuleType:
    spec = importlib.util.spec_from_file_location("m0011", MIGRATION)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


async def _table_state(conn) -> tuple[bool, str | None]:  # noqa: ANN001
    """Whether the table exists, and the delete rule of its layer FK."""
    exists = (
        await conn.execute(
            text("SELECT to_regclass(:name) IS NOT NULL"),
            {"name": f"{settings.SCHEMA}.layer_serial_counter"},
        )
    ).scalar()
    rule = (
        await conn.execute(
            text(
                "SELECT c.confdeltype FROM pg_constraint c "
                "WHERE c.conrelid = to_regclass(:name) AND c.contype = 'f'"
            ),
            {"name": f"{settings.SCHEMA}.layer_serial_counter"},
        )
    ).scalar()
    return bool(exists), rule


def test_the_model_matches_the_migration() -> None:
    table = LayerSerialCounter.__table__
    assert {c.name for c in table.columns} == {
        "layer_id",
        "field_name",
        "last_value",
        "updated_at",
    }
    assert {c.name for c in table.primary_key} == {"layer_id", "field_name"}
    (fk,) = table.c.layer_id.foreign_keys
    assert fk.ondelete == "CASCADE"
    # Declared against `customer`; the engine's schema_translate_map points it
    # at the active schema at run time.
    assert fk.target_fullname == "customer.layer.id"
    m = _load_migration()
    assert m.revision == "0011_layer_serial_counter"
    assert m.down_revision == "0010_support_tickets"


async def test_a_fresh_database_has_the_table_and_its_cascade() -> None:
    async with session_manager.connect() as conn:
        assert await _table_state(conn) == (True, "c")


async def test_migration_down_and_up() -> None:
    """Downgrade drops the table; upgrade recreates it with the cascade; a
    second upgrade on a database that has it (a fresh one, built from the
    models) changes nothing."""
    m = _load_migration()
    m.S = settings.SCHEMA

    def run(sync_conn, step) -> None:  # noqa: ANN001
        context = MigrationContext.configure(sync_conn)
        with Operations.context(context):
            step()

    async with session_manager.connect() as conn:
        await conn.run_sync(run, m.downgrade)
        assert await _table_state(conn) == (False, None)
        # Twice: guarded like every revision since the squashed baseline.
        await conn.run_sync(run, m.downgrade)

        await conn.run_sync(run, m.upgrade)
        assert await _table_state(conn) == (True, "c")
        await conn.run_sync(run, m.upgrade)
        assert await _table_state(conn) == (True, "c")
        await conn.commit()


async def test_purging_a_layer_removes_its_counters(
    fixture_create_user,  # noqa: ANN001
    fixture_get_home_folder,  # noqa: ANN001
) -> None:
    """The FK is what cleans up: a purge deletes the layer row, and its marks
    go with it, so nothing stale is left for a layer id that is gone."""
    s = settings.SCHEMA
    async with session_manager.connect() as conn:
        layer_id = (
            await conn.execute(
                text(
                    f"INSERT INTO {s}.layer "
                    "(id, name, type, user_id, folder_id, updated_at) "
                    "VALUES (gen_random_uuid(), 'serial', 'feature', :user, :folder, now()) "
                    "RETURNING id"
                ),
                {"user": fixture_create_user, "folder": fixture_get_home_folder["id"]},
            )
        ).scalar()
        await conn.execute(
            text(
                f"INSERT INTO {s}.layer_serial_counter "
                "(layer_id, field_name, last_value) VALUES (:id, 'nr', 41)"
            ),
            {"id": layer_id},
        )
        await conn.execute(
            text(f"DELETE FROM {s}.layer WHERE id = :id"), {"id": layer_id}
        )
        left = (
            await conn.execute(
                text(
                    f"SELECT count(*) FROM {s}.layer_serial_counter "
                    "WHERE layer_id = :id"
                ),
                {"id": layer_id},
            )
        ).scalar()
        await conn.commit()
    assert left == 0


async def test_a_filtered_copy_takes_the_sources_marks(
    fixture_create_user,  # noqa: ANN001
    fixture_get_home_folder,  # noqa: ANN001
) -> None:
    """``layer_create_filtered`` copies the source's marks with its
    field_config (goatlib's ``copy_layer_serial_counters``), so a copy never
    hands out a number the source handed out and deleted."""
    import asyncpg
    from goatlib.tools.db import ToolDatabaseService

    s = settings.SCHEMA
    async with session_manager.connect() as conn:
        ids = []
        for name in ("source", "copy"):
            ids.append(
                (
                    await conn.execute(
                        text(
                            f"INSERT INTO {s}.layer "
                            "(id, name, type, user_id, folder_id, updated_at) "
                            "VALUES (gen_random_uuid(), :name, 'feature', :user, "
                            ":folder, now()) RETURNING id"
                        ),
                        {
                            "name": name,
                            "user": fixture_create_user,
                            "folder": fixture_get_home_folder["id"],
                        },
                    )
                ).scalar()
            )
        source, copy = ids
        await conn.execute(
            text(
                f"INSERT INTO {s}.layer_serial_counter "
                "(layer_id, field_name, last_value) VALUES (:id, 'nr', 41)"
            ),
            {"id": source},
        )
        await conn.commit()

    pool = await asyncpg.create_pool(
        host=settings.POSTGRES_SERVER,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        database=settings.POSTGRES_DB,
        min_size=1,
        max_size=1,
    )
    try:
        db = ToolDatabaseService(pool, schema=s)
        await db.copy_layer_serial_counters(str(source), str(copy))
        # Twice is harmless: a mark never moves down.
        await db.copy_layer_serial_counters(str(source), str(copy))
        rows = await pool.fetch(
            f"SELECT field_name, last_value FROM {s}.layer_serial_counter "
            "WHERE layer_id = $1",
            copy,
        )
    finally:
        await pool.close()
    async with session_manager.connect() as conn:
        await conn.execute(
            text(f"DELETE FROM {s}.layer WHERE id = ANY(:ids)"), {"ids": ids}
        )
        await conn.commit()
    assert [(r["field_name"], r["last_value"]) for r in rows] == [("nr", 41)]
