"""DuckLake compaction task.

Where ``ducklake_maintenance`` reclaims space (expire snapshots + delete
catalog-tracked / filesystem orphans), THIS task addresses small-file
proliferation: tables that accumulate many tiny parquets from incremental
INSERTs (e.g., user feature edits, append-style syncs).

DuckLake's INSERT model is additive at the file level — every commit
writes a NEW parquet rather than merging into an existing one. After
30 individual feature adds, a layer has 1 big initial parquet + 30
tiny parquets, all ``end_snapshot=NULL`` (i.e. all "current"). Cleanup
won't touch them because they ARE the current data. To consolidate
them you need compaction.

Compaction here uses two DuckLake primitives:

  ``ducklake_merge_adjacent_files(catalog, schema, table, max_file_size, min_file_size)``
    Rewrites multiple small adjacent parquets into a single larger
    parquet. Small originals are marked ``end_snapshot=N`` (superseded).
    The merged parquet is the new current state.

  ``ducklake_cleanup_old_files(catalog, cleanup_all => true)``
    Same call ``ducklake_maintenance`` uses — physically deletes the
    files compaction just marked superseded. Run inline here so a
    single compaction execution actually frees disk, instead of waiting
    for the next maintenance pass.

Targeting: we only call ``merge_adjacent_files`` on tables that have
at least ``min_files_per_table`` current parquets AND at least one
of them is below ``small_file_threshold_mib``. Skip tables with one
big parquet (already optimal) and tables with a few big parquets
(merging produces no benefit, just I/O).

Safety properties (verified by tests and the safety check script):
  - Only "current" files (end_snapshot=NULL) are considered.
  - Compaction itself does not delete data — it rewrites + supersedes.
  - The optional cleanup_after step deletes superseded files, exactly
    the same safe path ``ducklake_maintenance`` uses.

Windmill path: f/goat/tasks/ducklake_compact
Worker tag: tools
Schedule: daily at 00:30 UTC, 30min after maintenance (registry.py)
"""

import logging
import sys
from typing import Any, Self

from pydantic import BaseModel, Field

from goatlib.config.postgres import TASKS_APPLICATION_NAME
from goatlib.storage import BaseDuckLakeManager
from goatlib.tools.base import ToolSettings
from goatlib.utils.credentials import postgres_attach_target

logger = logging.getLogger(__name__)


class DuckLakeCompactParams(BaseModel):
    """Parameters for the DuckLake compaction task.

    Per the DuckLake docs for ``ducklake_merge_adjacent_files``:
      - ``max_file_size`` (bytes): files at or larger than this are NOT
        compacted (already big enough). This is also the upper bound for
        merged output size.
      - ``min_file_size`` (bytes): files smaller than this are EXCLUDED
        (intentional noise floor — avoid compacting trivially-small files).
        Default 0 in DuckLake; we expose it for the rare case where a
        floor is desired.
      - ``max_compacted_files``: memory-control cap per table.
    """

    min_files_per_table: int = Field(
        default=3,
        ge=2,
        description=(
            "A table must have at least this many CURRENT parquets to be "
            "considered for compaction. Tables below this threshold are "
            "skipped (already consolidated)."
        ),
    )
    target_file_size_mib: int = Field(
        default=256,
        ge=1,
        description=(
            "Files smaller than this are eligible to be merged; merged "
            "output is bounded by this size. Maps directly to DuckLake's "
            "max_file_size parameter."
        ),
    )
    min_file_size_kib: int = Field(
        default=0,
        ge=0,
        description=(
            "Lower bound (KiB) — files smaller than this are excluded "
            "from compaction. Default 0 = include all small files. Set "
            "to a small positive value if you want to skip noise-level "
            "files (e.g., kB-size single-row parquets) until they "
            "accumulate further."
        ),
    )
    max_compacted_files: int | None = Field(
        default=None,
        description=(
            "Per-table cap on input files per compaction call (memory "
            "control). None = no cap (DuckLake default)."
        ),
    )
    cleanup_after: bool = Field(
        default=True,
        description=(
            "After merging, run ducklake_cleanup_old_files to physically "
            "delete the small parquets that merge_adjacent_files just "
            "marked superseded. Required to reclaim disk in one run — "
            "merge alone leaves the old files on disk."
        ),
    )
    max_tables: int | None = Field(
        default=None,
        description=(
            "Cap on how many tables to compact in one run. None = no cap. "
            "Useful at large catalog scale to bound run time."
        ),
    )
    dry_run: bool = Field(
        default=False,
        description="Identify candidates without doing any rewrites.",
    )


__all__ = ["DuckLakeCompactParams", "DuckLakeCompactTask", "main"]


class DuckLakeCompactTask:
    """Encapsulates the DuckLake compaction run."""

    def __init__(self: Self) -> None:
        self.settings: ToolSettings | None = None
        self._manager: BaseDuckLakeManager | None = None

    @staticmethod
    def _configure_logging_for_windmill() -> None:
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        h = logging.StreamHandler(sys.stdout)
        h.setLevel(logging.INFO)
        h.setFormatter(logging.Formatter("%(name)s - %(levelname)s - %(message)s"))
        root_logger.addHandler(h)

    def init_from_env(self: Self) -> None:
        self._configure_logging_for_windmill()
        self.settings = ToolSettings.from_env()

    def _get_manager(self: Self) -> BaseDuckLakeManager:
        if self._manager is None:
            if not self.settings:
                raise RuntimeError("Call init_from_env() before run()")
            # Read-write: compaction calls merge_adjacent_files and cleanup.
            self._manager = BaseDuckLakeManager(
                read_only=False, application_name=TASKS_APPLICATION_NAME
            )
            self._manager.init_from_params(
                postgres_uri=self.settings.ducklake_postgres_uri,
                storage_path=self.settings.ducklake_data_dir,
                catalog_schema=self.settings.ducklake_catalog_schema,
            )
        return self._manager

    @staticmethod
    def _find_candidates(
        con: Any,
        min_files_per_table: int,
        small_file_threshold_bytes: int,
    ) -> list[tuple[str, str, int, int, int]]:
        """Return (schema, table, n_current, n_small, small_bytes) tuples
        for tables that look worth compacting."""
        rows = con.execute(
            f"""
            SELECT
                s.schema_name,
                t.table_name,
                count(*) FILTER (WHERE df.end_snapshot IS NULL)
                    AS n_current,
                count(*) FILTER (
                    WHERE df.end_snapshot IS NULL
                      AND df.file_size_bytes < {small_file_threshold_bytes}
                ) AS n_small,
                COALESCE(sum(df.file_size_bytes) FILTER (
                    WHERE df.end_snapshot IS NULL
                      AND df.file_size_bytes < {small_file_threshold_bytes}
                ), 0) AS small_bytes
            FROM pg.ducklake.ducklake_data_file df
            JOIN pg.ducklake.ducklake_table t ON df.table_id = t.table_id
            JOIN pg.ducklake.ducklake_schema s ON t.schema_id = s.schema_id
            GROUP BY 1, 2
            HAVING count(*) FILTER (WHERE df.end_snapshot IS NULL)
                       >= {min_files_per_table}
               AND count(*) FILTER (
                   WHERE df.end_snapshot IS NULL
                     AND df.file_size_bytes < {small_file_threshold_bytes}
               ) >= 1
            ORDER BY n_small DESC, small_bytes DESC
            """
        ).fetchall()
        return [(r[0], r[1], int(r[2]), int(r[3]), int(r[4])) for r in rows]

    def run(self: Self, params: DuckLakeCompactParams) -> dict[str, Any]:
        manager = self._get_manager()
        target_bytes = params.target_file_size_mib * 1024 * 1024
        floor_bytes = params.min_file_size_kib * 1024

        with manager.connection() as con:
            # Need a postgres attach to query the catalog directly for
            # candidate selection (the ducklake-attached "lake" namespace
            # doesn't expose the metadata tables; the manager's own attach
            # only covers "lake.<schema>.<table>" queries).
            uri = postgres_attach_target(
                con,
                self.settings.ducklake_postgres_uri,  # type: ignore[union-attr]
            )
            con.execute(f"ATTACH IF NOT EXISTS 'postgres:{uri}' AS pg (READ_ONLY)")

            # Candidate filter: a table is a candidate iff it has at
            # least min_files_per_table CURRENT files AND at least one
            # is smaller than the target (else merging is a no-op).
            candidates = self._find_candidates(
                con,
                min_files_per_table=params.min_files_per_table,
                small_file_threshold_bytes=target_bytes,
            )
            if params.max_tables is not None:
                candidates = candidates[: params.max_tables]
            logger.info(
                "Found %d candidate table(s) (min_files=%d, target=%d MiB)",
                len(candidates),
                params.min_files_per_table,
                params.target_file_size_mib,
            )

            if params.dry_run:
                logger.info("DRY RUN — listing candidates only")
                return {
                    "dry_run": True,
                    "candidates": [
                        {
                            "schema": s,
                            "table": t,
                            "current_files": nc,
                            "small_files": ns,
                            "small_bytes": sb,
                        }
                        for s, t, nc, ns, sb in candidates
                    ],
                }

            # Per docs:
            # https://ducklake.select/docs/stable/duckdb/maintenance/merge_adjacent_files
            #   - positional args: catalog, table_name
            #   - schema is a NAMED kwarg
            #   - max_file_size = files >= this are skipped (already big);
            #     also the cap for merged output
            #   - min_file_size = files < this are skipped (noise floor)
            #   - max_compacted_files = memory cap per table
            # The function is a TABLE FUNCTION — must be invoked via
            # SELECT * FROM (not CALL). It returns one row per OUTPUT
            # file with columns (schema_name, table_name, files_processed,
            # files_created). Using CALL silently swallows the result set,
            # which is why we previously saw "0 tables compacted" while
            # the disk clearly shrank.
            extra_args = [f"max_file_size => {target_bytes}"]
            if floor_bytes > 0:
                extra_args.append(f"min_file_size => {floor_bytes}")
            if params.max_compacted_files is not None:
                extra_args.append(
                    f"max_compacted_files => {params.max_compacted_files}"
                )
            extra_sql = ", ".join(extra_args)

            tables_compacted = 0
            tables_unchanged = 0
            files_processed_total = 0
            files_created_total = 0
            failures: list[dict[str, str]] = []
            for schema, table, _nc, _ns, _sb in candidates:
                fq = f"lake.{schema}.{table}"
                try:
                    rows = con.execute(
                        "SELECT * FROM ducklake_merge_adjacent_files("
                        f"'lake', '{table}', "
                        f"schema => '{schema}', "
                        f"{extra_sql})"
                    ).fetchall()
                    files_processed = sum(r[2] for r in rows) if rows else 0
                    files_created = sum(r[3] for r in rows) if rows else 0
                    files_processed_total += files_processed
                    files_created_total += files_created
                    if files_processed > 0:
                        tables_compacted += 1
                        logger.info(
                            "Compacted %s: %d input files → %d output file(s)",
                            fq,
                            files_processed,
                            files_created,
                        )
                    else:
                        tables_unchanged += 1
                except Exception as e:
                    logger.warning("Compaction failed for %s: %s", fq, e)
                    failures.append({"table": fq, "error": str(e)})

            files_reclaimed = 0
            if params.cleanup_after:
                # Reclaim the small files compaction just marked
                # end_snapshot != NULL. Same call as ducklake_maintenance.
                deleted = con.execute(
                    "CALL ducklake_cleanup_old_files('lake', " "cleanup_all => true)"
                ).fetchall()
                files_reclaimed = len(deleted)
                logger.info(
                    "Reclaimed %d superseded file(s) from disk",
                    files_reclaimed,
                )

            return {
                "dry_run": False,
                "min_files_per_table": params.min_files_per_table,
                "target_file_size_mib": params.target_file_size_mib,
                "candidates": len(candidates),
                "tables_compacted": tables_compacted,
                "tables_unchanged": tables_unchanged,
                "files_processed": files_processed_total,
                "files_created": files_created_total,
                "files_reclaimed": files_reclaimed,
                "failures": failures,
            }

    def close(self: Self) -> None:
        if self._manager is not None:
            self._manager.close()


def main(
    params: DuckLakeCompactParams = DuckLakeCompactParams(),
) -> dict[str, Any]:
    """Windmill entry point for DuckLake compaction."""
    task = DuckLakeCompactTask()
    task.init_from_env()
    try:
        return task.run(params)
    finally:
        task.close()
