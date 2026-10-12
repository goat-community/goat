"""Purge trashed content past its retention period.

Soft-deleted rows (``deleted_at`` set by core's delete endpoints) stay
restorable for `retention_days`. This task removes what has aged out for
good: DuckLake tables first, so a failed data delete never leaves an
orphaned table behind a vanished metadata row, then the row itself and its
``resource_grant`` rows. Children go before parents — layers, templates,
projects and bundles are purged before folders, and a folder is only removed
once every live or still-trashed child inside it is gone (a folder with a
lingering child is simply skipped and picked up on a later run once that
child has been purged).
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Self
from uuid import UUID

import asyncpg
from pydantic import BaseModel, Field

from goatlib.config.postgres import TASKS_APPLICATION_NAME
from goatlib.tools.base import ToolSettings
from goatlib.tools.layer_delete_multi import (
    RECYCLE_DUCKDB_EVERY,
    LayerDeleteMultiRunner,
)

logger = logging.getLogger(__name__)

RETENTION_DAYS_DEFAULT = 30

#: Layer types backed by a DuckLake table. Other types (e.g. "raster") have
#: no per-layer DuckLake table to drop.
DUCKLAKE_LAYER_TYPES = ("feature", "table")

#: Resource types purged the same simple way: select past-retention rows,
#: delete their resource_grant rows, then the rows themselves. Templates go
#: first: a project template's frozen copy is a hidden `project` row the
#: template still points at, and purging the template releases that project
#: for the `project` pass in the same run.
SIMPLE_RESOURCE_TYPES = ("template", "project", "bundle")

#: Extra conditions a row must meet before its type is purged, keyed by
#: resource type and formatted with `schema`; the row is aliased `r`. A
#: project a live template points at holds that template's frozen payload
#: (`template.source_project_id` is ON DELETE SET NULL, and the copy is
#: hidden from trash), so purging it would leave the template with nothing
#: to instantiate.
PURGE_GUARDS = {
    "project": (
        "AND NOT EXISTS ("
        "SELECT 1 FROM {schema}.template t "
        "WHERE t.source_project_id = r.id AND t.deleted_at IS NULL) "
    ),
}


class PurgeTrashParams(BaseModel):
    """Parameters for the trash purge sweep."""

    retention_days: int = Field(
        default=RETENTION_DAYS_DEFAULT,
        ge=1,
        description="Delete rows soft-deleted more than this many days ago.",
    )
    batch_size: int = Field(
        default=500,
        ge=1,
        le=5000,
        description=(
            "Maximum rows selected per resource type per pass. Layers, "
            "projects and bundles run one pass per run; folders loop up "
            "to 10 passes per run, so a folder tree can purge more than "
            "this many rows in one run."
        ),
    )
    dry_run: bool = Field(
        default=False,
        description="Report what would be purged without deleting anything.",
    )


class PurgeTrashOutput(BaseModel):
    """Result of one purge sweep."""

    purged: dict[str, int] = Field(
        default_factory=lambda: {
            "layer": 0,
            "template": 0,
            "project": 0,
            "bundle": 0,
            "folder": 0,
        }
    )
    ducklake_deleted: int = 0
    skipped: int = 0
    dry_run: bool = False


class PurgeTrashTask:
    """Delete trashed content whose retention period has elapsed."""

    def __init__(self: Self) -> None:
        self.settings: ToolSettings | None = None

    def init_from_env(self: Self) -> None:
        self.settings = ToolSettings.from_env()

    async def _purge_layers(
        self: Self,
        conn: asyncpg.Connection,
        settings: ToolSettings,
        cutoff: datetime,
        params: PurgeTrashParams,
        out: PurgeTrashOutput,
    ) -> None:
        schema = settings.customer_schema
        rows = await conn.fetch(
            f"SELECT id, type, user_id FROM {schema}.layer "  # noqa: S608
            "WHERE deleted_at IS NOT NULL AND deleted_at < $1 "
            "ORDER BY deleted_at LIMIT $2",
            cutoff,
            params.batch_size,
        )
        if not rows:
            return

        deletable: list[UUID] = []
        # (layer_id, owner_id) for every feature/table layer, `owner_id`
        # None when the row has none — flat storage resolves the DuckLake
        # table by layer id alone (`resolve_layer_table_path`), so a missing
        # owner is no reason to skip its artifact cleanup; `owner_id` is
        # only ever passed through to `_delete_layer_artifacts` for its
        # legacy (owner-scoped) fallback path.
        ducklake_layers: list[tuple[UUID, UUID | None]] = []
        for row in rows:
            layer_id: UUID = row["id"]
            if row["type"] not in DUCKLAKE_LAYER_TYPES:
                deletable.append(layer_id)
            else:
                ducklake_layers.append((layer_id, row["user_id"]))

        if ducklake_layers:
            if params.dry_run:
                # Preview only: report as would-be-purged without touching
                # DuckLake.
                deletable.extend(layer_id for layer_id, _owner in ducklake_layers)
            else:
                runner = LayerDeleteMultiRunner()
                try:
                    runner.init(settings)
                    for processed, (layer_id, owner_id) in enumerate(
                        ducklake_layers, start=1
                    ):
                        try:
                            ducklake_ok, pmtiles_ok = runner._delete_layer_artifacts(  # noqa: SLF001
                                str(layer_id), str(owner_id) if owner_id else ""
                            )
                        except Exception as e:  # noqa: BLE001 - keep sweeping
                            out.skipped += 1
                            logger.warning(
                                "Skipping layer %s: artifact delete raised: %s",
                                layer_id,
                                e,
                            )
                        else:
                            if ducklake_ok:
                                out.ducklake_deleted += 1
                            if ducklake_ok and pmtiles_ok:
                                deletable.append(layer_id)
                            else:
                                # _delete_ducklake_table / _delete_pmtiles
                                # both return True for "already gone" as well
                                # as "just deleted" — a genuine False here
                                # means an actual error prevented checking or
                                # removing the artifact, so the row stays for
                                # a retry rather than risk deleting a row
                                # whose data or tiles are still on disk.
                                out.skipped += 1
                                logger.warning(
                                    "Skipping layer %s: artifact delete "
                                    "reported failure (ducklake=%s, pmtiles=%s)",
                                    layer_id,
                                    ducklake_ok,
                                    pmtiles_ok,
                                )

                        # Each DROP TABLE is a DuckLake commit whose memory
                        # cost accumulates on the connection; recycle at the
                        # same cadence LayerDeleteMultiRunner.run uses so a
                        # large purge batch doesn't OOM the worker either.
                        if processed % RECYCLE_DUCKDB_EVERY == 0:
                            runner.recycle_duckdb_connection()
                finally:
                    runner.cleanup()

        if not deletable:
            return
        if params.dry_run:
            out.purged["layer"] = len(deletable)
            return

        await conn.execute(
            f"DELETE FROM {schema}.resource_grant "  # noqa: S608
            "WHERE resource_type = 'layer' AND resource_id = ANY($1::uuid[])",
            deletable,
        )
        await conn.execute(
            f"DELETE FROM {schema}.layer "  # noqa: S608
            "WHERE id = ANY($1::uuid[]) AND deleted_at IS NOT NULL",
            deletable,
        )
        out.purged["layer"] = len(deletable)

    async def _purge_simple_resource(
        self: Self,
        conn: asyncpg.Connection,
        settings: ToolSettings,
        resource_type: str,
        cutoff: datetime,
        params: PurgeTrashParams,
        out: PurgeTrashOutput,
    ) -> None:
        schema = settings.customer_schema
        guard = PURGE_GUARDS.get(resource_type, "").format(schema=schema)
        rows = await conn.fetch(
            f"SELECT r.id FROM {schema}.{resource_type} r "  # noqa: S608
            "WHERE r.deleted_at IS NOT NULL AND r.deleted_at < $1 "
            f"{guard}"
            "ORDER BY r.deleted_at LIMIT $2",
            cutoff,
            params.batch_size,
        )
        ids = [row["id"] for row in rows]
        out.purged[resource_type] = len(ids)
        if not ids or params.dry_run:
            return

        await conn.execute(
            f"DELETE FROM {schema}.resource_grant "  # noqa: S608
            f"WHERE resource_type = '{resource_type}' "
            "AND resource_id = ANY($1::uuid[])",
            ids,
        )
        await conn.execute(
            f"DELETE FROM {schema}.{resource_type} "  # noqa: S608
            "WHERE id = ANY($1::uuid[]) AND deleted_at IS NOT NULL",
            ids,
        )

    #: Safety bound on how many leaf-then-parent passes one run makes over
    #: the folder tree — a trashed subtree this deep clears in one run
    #: instead of one level per day; deeper than this is vanishingly
    #: unlikely and simply picks up the remaining levels on the next run.
    _MAX_FOLDER_PASSES = 10

    async def _purge_empty_folders(
        self: Self,
        conn: asyncpg.Connection,
        settings: ToolSettings,
        cutoff: datetime,
        params: PurgeTrashParams,
        out: PurgeTrashOutput,
    ) -> None:
        schema = settings.customer_schema
        total_deleted = 0
        for _ in range(self._MAX_FOLDER_PASSES):
            rows = await conn.fetch(
                f"""
                SELECT f.id FROM {schema}.folder f
                WHERE f.deleted_at IS NOT NULL AND f.deleted_at < $1
                  AND NOT EXISTS (
                      SELECT 1 FROM {schema}.layer l WHERE l.folder_id = f.id
                  )
                  AND NOT EXISTS (
                      SELECT 1 FROM {schema}.project p WHERE p.folder_id = f.id
                  )
                  AND NOT EXISTS (
                      SELECT 1 FROM {schema}.bundle b WHERE b.folder_id = f.id
                  )
                  AND NOT EXISTS (
                      SELECT 1 FROM {schema}.template t WHERE t.folder_id = f.id
                  )
                  AND NOT EXISTS (
                      SELECT 1 FROM {schema}.folder c WHERE c.parent_id = f.id
                  )
                ORDER BY f.deleted_at
                LIMIT $2
                """,  # noqa: S608
                cutoff,
                params.batch_size,
            )
            ids = [row["id"] for row in rows]
            if not ids:
                break
            total_deleted += len(ids)
            if params.dry_run:
                # A dry run never deletes, so a second pass would just see
                # the same leaves again — one preview pass is enough.
                break

            await conn.execute(
                f"DELETE FROM {schema}.resource_grant "  # noqa: S608
                "WHERE resource_type = 'folder' AND resource_id = ANY($1::uuid[])",
                ids,
            )
            await conn.execute(
                f"DELETE FROM {schema}.folder "  # noqa: S608
                "WHERE id = ANY($1::uuid[]) AND deleted_at IS NOT NULL",
                ids,
            )
        out.purged["folder"] = total_deleted

    async def _run(self: Self, params: PurgeTrashParams) -> PurgeTrashOutput:
        assert self.settings is not None
        settings = self.settings
        cutoff = datetime.now(timezone.utc) - timedelta(days=params.retention_days)
        out = PurgeTrashOutput(dry_run=params.dry_run)

        conn = await asyncpg.connect(
            **settings.postgres_connect_args(TASKS_APPLICATION_NAME),
        )
        try:
            # Layers first: dropping a layer's DuckLake table must happen
            # before its row is deleted, so a crash between the two leaves
            # only a metadata row for the next run to retry — never data
            # with nothing left to name it.
            await self._purge_layers(conn, settings, cutoff, params, out)
            for resource_type in SIMPLE_RESOURCE_TYPES:
                await self._purge_simple_resource(
                    conn, settings, resource_type, cutoff, params, out
                )
            # Folders last: the NOT EXISTS guards mean a folder purges only
            # once every layer/template/project/bundle/subfolder inside it
            # is gone.
            await self._purge_empty_folders(conn, settings, cutoff, params, out)
        finally:
            await conn.close()
        return out

    def run(self: Self, params: PurgeTrashParams) -> PurgeTrashOutput:
        if self.settings is None:
            raise RuntimeError("Call init_from_env() before running task")
        return asyncio.new_event_loop().run_until_complete(self._run(params))


def main(params: PurgeTrashParams) -> dict[str, Any]:
    """Windmill entry point."""
    task = PurgeTrashTask()
    task.init_from_env()
    return task.run(params).model_dump()
