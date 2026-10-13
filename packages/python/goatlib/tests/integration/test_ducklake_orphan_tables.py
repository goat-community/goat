"""The orphan-table sweep against a real DuckLake catalog.

Everything lives in throwaway schemas: the DuckLake catalog of `lake_env` and
a customer schema holding a minimal `layer` table. Ages come from the
catalog's own snapshots, moved back in time here.

Run explicitly with:
    uv run pytest tests/integration/test_ducklake_orphan_tables.py -m integration -v
"""

import asyncio
import os
import uuid
from pathlib import Path
from typing import Any, Iterator

import asyncpg
import pytest
from goatlib.io.pmtiles import PMTilesGenerator
from goatlib.storage import BaseDuckLakeManager
from goatlib.tasks.ducklake_orphan_tables import (
    DuckLakeOrphanTablesOutput,
    DuckLakeOrphanTablesParams,
    DuckLakeOrphanTablesTask,
)
from goatlib.tools.base import ToolSettings
from goatlib.utils.layer import layer_id_to_table_name

pytestmark = pytest.mark.integration

OLD_ORPHAN = "a0000000-0000-4000-8000-000000000001"
LEGACY_ORPHAN = "a0000000-0000-4000-8000-000000000002"
RECORDED = "a0000000-0000-4000-8000-000000000003"
TRASHED = "a0000000-0000-4000-8000-000000000004"
YOUNG_ORPHAN = "a0000000-0000-4000-8000-000000000005"


def _pg() -> dict[str, Any]:
    return {
        "host": os.getenv("POSTGRES_SERVER", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "database": os.getenv("POSTGRES_DB", "goat"),
    }


def _sql(statement: str, *args: Any) -> list[asyncpg.Record]:
    async def run() -> list[asyncpg.Record]:
        conn = await asyncpg.connect(**_pg())
        try:
            return await conn.fetch(statement, *args)
        finally:
            await conn.close()

    return asyncio.run(run())


def _table(writer: BaseDuckLakeManager, layer_id: str, schema: str = "main") -> None:
    # Enough rows for a data file: DuckLake keeps a few rows in the catalog.
    writer.execute(
        f"CREATE TABLE lake.{schema}.{layer_id_to_table_name(layer_id)} "
        "AS SELECT range AS x FROM range(10000)"
    )


class _Env:
    def __init__(self, settings: ToolSettings, catalog: str, customer: str) -> None:
        self.settings = settings
        self.catalog = catalog
        self.customer = customer

    def live_tables(self) -> set[str]:
        return {
            f"{r['schema_name']}.{r['table_name']}"
            for r in _sql(
                f"SELECT s.schema_name, t.table_name FROM {self.catalog}.ducklake_table t "
                f"JOIN {self.catalog}.ducklake_schema s ON s.schema_id = t.schema_id "
                "WHERE t.end_snapshot IS NULL AND s.end_snapshot IS NULL"
            )
        }

    def task(self) -> DuckLakeOrphanTablesTask:
        task = DuckLakeOrphanTablesTask()
        task.settings = self.settings
        return task

    def run(self, **params: Any) -> DuckLakeOrphanTablesOutput:
        return self.task().run(DuckLakeOrphanTablesParams(**params))

    def tiles(self, layer_id: str) -> Path:
        return PMTilesGenerator(self.settings.tiles_data_dir).get_pmtiles_path(layer_id)


@pytest.fixture()
def env(lake_env: tuple[Any, BaseDuckLakeManager], tmp_path: Path) -> Iterator[_Env]:
    """Five layer tables in a throwaway catalog, three without a layer row.

    Created in this order, then every snapshot so far moved three days back,
    and the snapshot that created OLD_ORPHAN expired the way
    ducklake_maintenance expires it; the young orphan comes after that.
    """
    tmp_settings, writer = lake_env
    catalog = tmp_settings.DUCKLAKE_CATALOG_SCHEMA
    customer = f"orphans_test_{uuid.uuid4().hex[:8]}"
    # Never anything but the throwaway schemas this test made.
    assert catalog.startswith("ducklake_test_")
    assert customer.startswith("orphans_test_")

    _sql(f"CREATE SCHEMA {customer}")
    _sql(
        f"CREATE TABLE {customer}.layer "
        "(id uuid PRIMARY KEY, deleted_at timestamptz)"
    )
    try:
        writer.execute("CREATE SCHEMA lake.user_abc")
        _table(writer, OLD_ORPHAN)
        _table(writer, LEGACY_ORPHAN, schema="user_abc")
        _table(writer, RECORDED)
        _table(writer, TRASHED)
        _sql(
            f"INSERT INTO {customer}.layer VALUES ($1, NULL), ($2, now())",
            uuid.UUID(RECORDED),
            uuid.UUID(TRASHED),
        )
        _sql(
            f"UPDATE {catalog}.ducklake_snapshot "
            "SET snapshot_time = snapshot_time - interval '3 days'"
        )
        (created,) = _sql(
            f"SELECT begin_snapshot FROM {catalog}.ducklake_table "
            "WHERE table_name = $1",
            layer_id_to_table_name(OLD_ORPHAN),
        )
        writer.execute(
            "CALL ducklake_expire_snapshots('lake', "
            f"versions => [{created['begin_snapshot']}])"
        )
        assert not _sql(
            f"SELECT 1 FROM {catalog}.ducklake_snapshot WHERE snapshot_id = $1",
            created["begin_snapshot"],
        ), "the creating snapshot should be expired"
        _table(writer, YOUNG_ORPHAN)

        p = _pg()
        settings = ToolSettings(
            postgres_server=p["host"],
            postgres_port=p["port"],
            postgres_user=p["user"],
            postgres_password=p["password"],
            postgres_db=p["database"],
            ducklake_postgres_uri=tmp_settings.POSTGRES_DATABASE_URI,
            ducklake_catalog_schema=catalog,
            ducklake_data_dir=str(tmp_settings.DUCKLAKE_DATA_DIR),
            customer_schema=customer,
            tiles_data_dir=str(tmp_path / "tiles"),
            pmtiles_enabled=False,
        )
        env = _Env(settings, catalog, customer)
        for layer_id in (OLD_ORPHAN, RECORDED):
            path = env.tiles(layer_id)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"tiles")
        yield env
    finally:
        _sql(f"DROP SCHEMA IF EXISTS {customer} CASCADE")


ALL_TABLES = {
    "main.t_first",
    f"main.{layer_id_to_table_name(OLD_ORPHAN)}",
    f"user_abc.{layer_id_to_table_name(LEGACY_ORPHAN)}",
    f"main.{layer_id_to_table_name(RECORDED)}",
    f"main.{layer_id_to_table_name(TRASHED)}",
    f"main.{layer_id_to_table_name(YOUNG_ORPHAN)}",
}


def test_a_report_lists_the_orphans_and_changes_nothing(env: _Env) -> None:
    out = env.run()

    assert out.layer_tables == 5  # `t_first` is no layer's table
    by_layer = {t.layer_id: t for t in out.tables}
    assert set(by_layer) == {OLD_ORPHAN, LEGACY_ORPHAN, YOUNG_ORPHAN}
    assert by_layer[LEGACY_ORPHAN].table.startswith("user_abc.")
    # Its creating snapshot is gone: the next one kept still dates it.
    assert by_layer[OLD_ORPHAN].created_by is not None
    assert by_layer[OLD_ORPHAN].old_enough
    assert by_layer[LEGACY_ORPHAN].old_enough
    assert not by_layer[YOUNG_ORPHAN].old_enough
    assert out.old_enough == 2
    assert all(t.files == 1 and t.bytes > 0 for t in out.tables)
    assert out.dropped == 0
    assert env.live_tables() == ALL_TABLES
    assert env.tiles(OLD_ORPHAN).exists()


def test_dropping_takes_only_old_orphans(env: _Env) -> None:
    out = env.run(drop_tables=True, abort_pct=100)

    assert out.aborted is None
    assert out.dropped == 2
    assert {t.layer_id for t in out.tables if t.dropped} == {OLD_ORPHAN, LEGACY_ORPHAN}
    assert env.live_tables() == ALL_TABLES - {
        f"main.{layer_id_to_table_name(OLD_ORPHAN)}",
        f"user_abc.{layer_id_to_table_name(LEGACY_ORPHAN)}",
    }
    # The orphan's tiles go with it; a recorded layer's stay.
    assert not env.tiles(OLD_ORPHAN).exists()
    assert env.tiles(RECORDED).exists()


def test_too_many_orphans_drop_nothing(env: _Env) -> None:
    """Three of five layer tables without a record looks like a wrong
    schema, not like failed runs."""
    out = env.run(drop_tables=True)

    assert out.aborted is not None and "abort_pct" in out.aborted
    assert out.dropped == 0
    assert env.live_tables() == ALL_TABLES


def test_an_empty_layer_table_drops_nothing(env: _Env) -> None:
    _sql(f"DELETE FROM {env.customer}.layer")

    out = env.run(drop_tables=True, abort_pct=100)

    assert out.aborted is not None and "no rows" in out.aborted
    assert env.live_tables() == ALL_TABLES


def test_max_drops_bounds_a_run(env: _Env) -> None:
    out = env.run(drop_tables=True, abort_pct=100, max_drops=1)

    assert out.dropped == 1
    assert len(env.live_tables()) == len(ALL_TABLES) - 1


def test_a_table_recorded_since_the_scan_is_kept(env: _Env) -> None:
    """The DROP re-checks each table: a row written after the scan wins."""
    task = env.task()
    params = DuckLakeOrphanTablesParams(drop_tables=True, abort_pct=100)

    async def run() -> DuckLakeOrphanTablesOutput:
        out = DuckLakeOrphanTablesOutput(drop_tables=True)
        conn = await asyncpg.connect(**_pg())
        try:
            rows, _ = await task._find(conn, params, out)
            await conn.execute(
                f"INSERT INTO {env.customer}.layer VALUES ($1, NULL)",
                uuid.UUID(OLD_ORPHAN),
            )
            await task._drop(conn, rows, params, out)
        finally:
            await conn.close()
        return out

    out = asyncio.run(run())

    assert out.skipped == 1
    assert out.dropped == 1
    assert f"main.{layer_id_to_table_name(OLD_ORPHAN)}" in env.live_tables()


def test_a_table_created_again_since_the_scan_is_kept(
    env: _Env, lake_env: tuple[Any, BaseDuckLakeManager]
) -> None:
    """Same name, but a new table: it was created after the scan, so it is
    young whatever the scan said about the old one."""
    _, writer = lake_env
    task = env.task()
    params = DuckLakeOrphanTablesParams(drop_tables=True, abort_pct=100)

    async def run() -> DuckLakeOrphanTablesOutput:
        out = DuckLakeOrphanTablesOutput(drop_tables=True)
        conn = await asyncpg.connect(**_pg())
        try:
            rows, _ = await task._find(conn, params, out)
            writer.execute(f"DROP TABLE lake.main.{layer_id_to_table_name(OLD_ORPHAN)}")
            _table(writer, OLD_ORPHAN)
            await task._drop(conn, rows, params, out)
        finally:
            await conn.close()
        return out

    out = asyncio.run(run())

    assert out.skipped == 1
    assert f"main.{layer_id_to_table_name(OLD_ORPHAN)}" in env.live_tables()
