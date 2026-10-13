"""Find, and on request drop, DuckLake layer tables no layer record points to.

A tool run writes its result table (``t_<layer id>``) before it saves the layer
record. A run that fails in between drops the table again
(``SimpleToolRunner.drop_unrecorded_tables``), but a killed one cannot: a
cancelled Windmill job is killed outright, and so is a worker that runs out of
memory. Its table stays in DuckLake with nothing pointing to it: it never shows
in the app, nobody can delete it, and its files and catalog rows are kept for
good. ``purge_trash`` starts from layer records and ``ducklake_maintenance``
only reclaims files no live table uses, so neither reaches it.

An orphan is a live table named ``t_<32 hex>``, in any DuckLake schema (older
layers still sit in per-user schemas), whose id no row of the customer
schema's ``layer`` table carries. Trashed rows count as rows: their tables are
``purge_trash``'s. Every DuckLake table so named belongs to a layer; catalog
layers, workflow previews and PMTiles are files, not DuckLake tables.

A running job's table has no row yet either, so a table only counts as an
orphan once it is older than ``min_age_hours``: a day at least, far longer
than the workers let a job run (``JOB_DEFAULT_TIMEOUT``). Its age is the time
of the snapshot that created it, or, once ``ducklake_maintenance`` has expired
that snapshot, of the next snapshot still kept: later than the creation, so
the age is never overstated. A table whose age cannot be told that way is
never dropped.

Reports by default and changes nothing; the report reads the catalog and the
layer table in one read-only transaction. ``drop_tables`` drops the old
orphans, at most ``max_drops`` per run. Right before its DROP each one is
checked again: still without a layer row, and still the same table (id and
creating snapshot) in the catalog the DROP goes to. It drops nothing when the
layer table is empty or the orphans are more than ``abort_pct`` of all layer
tables: that many points at a wrong ``SCHEMA`` or a catalog of another
database, not at failed runs. The rule assumes the catalog holds this
deployment's layers only, which is how GOAT is deployed.
"""

import asyncio
import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Self

import asyncpg
from pydantic import BaseModel, Field

from goatlib.config.postgres import TASKS_APPLICATION_NAME
from goatlib.storage.ducklake import fetch_one
from goatlib.tools.base import SimpleToolRunner, ToolSettings
from goatlib.tools.layer_delete_multi import RECYCLE_DUCKDB_EVERY
from goatlib.utils.layer import normalize_layer_id

logger = logging.getLogger(__name__)

#: The tables a layer owns: `layer_id_to_table_name`.
LAYER_TABLE_PATTERN = "^t_[0-9a-f]{32}$"

#: A DuckLake schema name safe to quote into a DROP statement.
_SCHEMA_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

MIN_AGE_HOURS = 24


class DuckLakeOrphanTablesParams(BaseModel):
    """Parameters for the orphan-table sweep."""

    drop_tables: bool = Field(
        default=False,
        description=(
            "Drop the orphan tables older than min_age_hours, and their "
            "PMTiles. Off: report them and change nothing."
        ),
    )
    min_age_hours: int = Field(
        default=MIN_AGE_HOURS,
        ge=MIN_AGE_HOURS,
        description=(
            "Only tables created longer ago than this count as orphans when "
            "dropping; a younger one may belong to a job still running."
        ),
    )
    max_drops: int = Field(
        default=500,
        ge=1,
        le=10000,
        description=(
            "Drop at most this many tables per run; later runs take the rest. "
            "Every DROP is a DuckLake commit."
        ),
    )
    abort_pct: float = Field(
        default=10.0,
        ge=0.0,
        le=100.0,
        description=(
            "Drop nothing when the orphans are more than this percentage of "
            "all layer tables: that many points at a wrong SCHEMA or a catalog "
            "of another database rather than at failed runs. Raise it once, "
            "after reading the report, to clear a known backlog."
        ),
    )


class OrphanTable(BaseModel):
    """One live layer table without a layer record."""

    table: str = Field(description="<DuckLake schema>.<table>")
    layer_id: str
    created_by: datetime | None = Field(
        default=None,
        description=(
            "The table existed by then: the time of its creating snapshot, or "
            "of the next one kept. None when no snapshot tells."
        ),
    )
    old_enough: bool = False
    files: int = 0
    bytes: int = 0
    dropped: bool = False


class DuckLakeOrphanTablesOutput(BaseModel):
    """Result of one sweep."""

    drop_tables: bool = False
    layer_tables: int = Field(0, description="Live t_<id> tables in DuckLake")
    orphans: int = 0
    old_enough: int = Field(0, description="Orphans older than min_age_hours")
    orphan_bytes: int = 0
    dropped: int = 0
    skipped: int = 0
    aborted: str | None = Field(
        default=None,
        description=(
            "Why a run with drop_tables drops nothing; a report says it too, "
            "so the guard can be checked before dropping."
        ),
    )
    tables: list[OrphanTable] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


def _orphans_sql(catalog: str, customer: str) -> str:
    # The uuid cast sits behind the CASE so it only sees names that matched.
    return f"""
        SELECT s.schema_name, t.table_name, t.table_id, t.begin_snapshot,
               (SELECT sn.snapshot_time FROM {catalog}.ducklake_snapshot sn
                 WHERE sn.snapshot_id >= t.begin_snapshot
                 ORDER BY sn.snapshot_id LIMIT 1) AS created_by
        FROM {catalog}.ducklake_table t
        JOIN {catalog}.ducklake_schema s
          ON s.schema_id = t.schema_id AND s.end_snapshot IS NULL
        WHERE t.end_snapshot IS NULL
          AND t.table_name ~ '{LAYER_TABLE_PATTERN}'
          AND NOT EXISTS (
              SELECT 1 FROM {customer}.layer l
              WHERE l.id = CASE WHEN t.table_name ~ '{LAYER_TABLE_PATTERN}'
                                THEN substr(t.table_name, 3)::uuid END
          )
        ORDER BY t.begin_snapshot, t.table_id
    """  # noqa: S608


def _layer_tables_sql(catalog: str) -> str:
    return f"""
        SELECT count(*) FROM {catalog}.ducklake_table t
        JOIN {catalog}.ducklake_schema s
          ON s.schema_id = t.schema_id AND s.end_snapshot IS NULL
        WHERE t.end_snapshot IS NULL AND t.table_name ~ '{LAYER_TABLE_PATTERN}'
    """  # noqa: S608


def _sizes_sql(catalog: str) -> str:
    return f"""
        SELECT table_id, count(*) AS files,
               COALESCE(sum(file_size_bytes), 0) AS bytes
        FROM {catalog}.ducklake_data_file
        WHERE end_snapshot IS NULL AND table_id = ANY($1::bigint[])
        GROUP BY table_id
    """  # noqa: S608


def _same_live_table_sql(catalog: str) -> str:
    """The table, still live and still created by the same snapshot, read
    through the DuckLake attach the DROP goes to."""
    return f"""
        SELECT 1 FROM __ducklake_metadata_lake.{catalog}.ducklake_table
        WHERE table_id = ? AND table_name = ? AND begin_snapshot = ?
          AND end_snapshot IS NULL
    """  # noqa: S608


class DuckLakeOrphanTablesTask:
    """Report, and on request drop, layer tables without a layer record."""

    def __init__(self: Self) -> None:
        self.settings: ToolSettings | None = None

    def init_from_env(self: Self) -> None:
        # The report is the log as much as the result.
        SimpleToolRunner._configure_logging_for_windmill()  # noqa: SLF001
        self.settings = ToolSettings.from_env()

    async def _find(
        self: Self,
        conn: asyncpg.Connection,
        params: DuckLakeOrphanTablesParams,
        out: DuckLakeOrphanTablesOutput,
    ) -> tuple[list[asyncpg.Record], int]:
        """The orphan rows and the number of layer rows, read in one
        read-only transaction so both describe the same moment."""
        assert self.settings is not None
        catalog = self.settings.ducklake_catalog_schema
        customer = self.settings.customer_schema
        async with conn.transaction(readonly=True):
            layer_rows = await conn.fetchval(
                f"SELECT count(*) FROM {customer}.layer"  # noqa: S608
            )
            out.layer_tables = await conn.fetchval(_layer_tables_sql(catalog))
            rows = await conn.fetch(_orphans_sql(catalog, customer))
            sizes = {
                r["table_id"]: r
                for r in await conn.fetch(
                    _sizes_sql(catalog), [r["table_id"] for r in rows]
                )
            }

        cutoff = datetime.now(timezone.utc) - timedelta(hours=params.min_age_hours)
        for row in rows:
            size = sizes.get(row["table_id"])
            created_by = row["created_by"]
            entry = OrphanTable(
                table=f"{row['schema_name']}.{row['table_name']}",
                layer_id=normalize_layer_id(row["table_name"][2:]),
                created_by=created_by,
                old_enough=created_by is not None and created_by < cutoff,
                files=int(size["files"]) if size else 0,
                bytes=int(size["bytes"]) if size else 0,
            )
            out.tables.append(entry)
            out.orphan_bytes += entry.bytes
            out.old_enough += entry.old_enough
            # Every orphan is in the result; the log keeps the summary below.
            logger.debug(
                "Orphan %s (layer %s): created by %s, %d files, %d bytes%s",
                entry.table,
                entry.layer_id,
                created_by.isoformat() if created_by else "unknown",
                entry.files,
                entry.bytes,
                "" if entry.old_enough else ", too young to drop",
            )
        out.orphans = len(rows)
        return list(rows), int(layer_rows)

    def _abort_reason(
        self: Self,
        params: DuckLakeOrphanTablesParams,
        out: DuckLakeOrphanTablesOutput,
        layer_rows: int,
    ) -> str | None:
        assert self.settings is not None
        if layer_rows == 0:
            return (
                f"{self.settings.customer_schema}.layer has no rows: every "
                "table would look orphaned. Is SCHEMA set to the right schema?"
            )
        share = 100.0 * out.orphans / out.layer_tables if out.layer_tables else 0.0
        if share > params.abort_pct:
            return (
                f"{out.orphans} of {out.layer_tables} layer tables ({share:.1f}%) "
                f"have no layer record, more than abort_pct={params.abort_pct}. "
                "Check SCHEMA and the DuckLake catalog before raising abort_pct."
            )
        return None

    async def _drop(
        self: Self,
        conn: asyncpg.Connection,
        rows: list[asyncpg.Record],
        params: DuckLakeOrphanTablesParams,
        out: DuckLakeOrphanTablesOutput,
    ) -> None:
        assert self.settings is not None
        catalog = self.settings.ducklake_catalog_schema
        customer = self.settings.customer_schema
        entries = {entry.table: entry for entry in out.tables}
        runner = SimpleToolRunner()
        runner.init(self.settings)
        drops = 0
        try:
            for row in rows:
                entry = entries[f"{row['schema_name']}.{row['table_name']}"]
                if not entry.old_enough:
                    continue
                if drops >= params.max_drops:
                    logger.info("Reached max_drops=%d", params.max_drops)
                    break
                if not _SCHEMA_NAME.match(row["schema_name"]):
                    out.skipped += 1
                    out.errors.append(f"{entry.table}: unexpected schema name")
                    continue
                recorded = await conn.fetchval(
                    f"SELECT 1 FROM {customer}.layer WHERE id = $1::uuid",  # noqa: S608
                    entry.layer_id,
                )
                same = fetch_one(
                    runner.duckdb_con,
                    _same_live_table_sql(catalog),
                    [row["table_id"], row["table_name"], row["begin_snapshot"]],
                )
                if recorded or not same:
                    out.skipped += 1
                    logger.info(
                        "Skipped %s: %s since the scan",
                        entry.table,
                        "recorded" if recorded else "changed or gone",
                    )
                    continue
                drops += 1
                try:
                    runner.duckdb_con.execute(
                        f'DROP TABLE IF EXISTS lake."{row["schema_name"]}".'
                        f'"{row["table_name"]}"'
                    )
                except Exception as e:  # noqa: BLE001 - keep sweeping
                    out.skipped += 1
                    out.errors.append(f"{entry.table}: {e}")
                    logger.warning("Could not drop %s: %s", entry.table, e)
                    runner.recycle_duckdb_connection()
                    continue
                entry.dropped = True
                out.dropped += 1
                logger.info("Dropped %s", entry.table)
                runner._delete_new_pmtiles(entry.layer_id)  # noqa: SLF001
                # Each DROP is a DuckLake commit whose catalog cache stays on
                # the connection; recycle like purge_trash does.
                if drops % RECYCLE_DUCKDB_EVERY == 0:
                    runner.recycle_duckdb_connection()
        finally:
            runner.cleanup()

    async def _run(
        self: Self, params: DuckLakeOrphanTablesParams
    ) -> DuckLakeOrphanTablesOutput:
        assert self.settings is not None
        out = DuckLakeOrphanTablesOutput(drop_tables=params.drop_tables)
        conn = await asyncpg.connect(
            **self.settings.postgres_connect_args(TASKS_APPLICATION_NAME),
        )
        try:
            rows, layer_rows = await self._find(conn, params, out)
            logger.info(
                "%d of %d layer tables have no layer record (%d bytes); "
                "%d older than %d hours",
                out.orphans,
                out.layer_tables,
                out.orphan_bytes,
                out.old_enough,
                params.min_age_hours,
            )
            out.aborted = self._abort_reason(params, out, layer_rows)
            if not params.drop_tables:
                if out.aborted:
                    logger.warning(
                        "A run with drop_tables would drop nothing: %s", out.aborted
                    )
                return out
            if out.aborted:
                logger.error("Dropping nothing: %s", out.aborted)
                return out
            await self._drop(conn, rows, params, out)
            logger.info(
                "Dropped %d orphan tables, skipped %d", out.dropped, out.skipped
            )
        finally:
            await conn.close()
        return out

    def run(
        self: Self, params: DuckLakeOrphanTablesParams
    ) -> DuckLakeOrphanTablesOutput:
        if self.settings is None:
            raise RuntimeError("Call init_from_env() before running task")
        return asyncio.run(self._run(params))


def main(
    params: DuckLakeOrphanTablesParams = DuckLakeOrphanTablesParams(),
) -> dict[str, Any]:
    """Windmill entry point."""
    task = DuckLakeOrphanTablesTask()
    task.init_from_env()
    return task.run(params).model_dump(mode="json")
