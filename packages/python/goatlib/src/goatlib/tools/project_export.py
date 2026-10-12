"""Project export tool — produces a self-contained ZIP archive.

Gathers project metadata directly from PostgreSQL, reads layer data from
DuckLake, fetches S3 assets, and assembles the ZIP.

Usage (Windmill entry point):
    result = main(ProjectExportParams(...))
    # result = {"s3_key": "exports/user_id/...", "presigned_url": "https://..."}
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import tempfile
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Self

import asyncpg
import duckdb
from pydantic import BaseModel, Field

from goatlib.tools.base import SimpleToolRunner
from goatlib.tools.project_schemas import (
    EXTERNAL_DATA_TYPES,
    FORMAT_VERSION,
    ExportManifest,
)
from goatlib.tools.schemas import ToolInputBase
from goatlib.utils.layer import (
    quoted_relation,
)
from goatlib.utils.workflow_layers import drop_layer_refs, workflow_layer_refs

logger = logging.getLogger(__name__)


class ProjectExportParams(ToolInputBase):
    """Parameters for project export tool."""

    source_instance: str | None = Field(None, description="Source GOAT instance URL")


class ProjectExportOutput(BaseModel):
    """Output of project export."""

    s3_key: str
    presigned_url: str
    download_url: str = ""  # Alias for presigned_url, used by jobs panel
    file_name: str = ""  # Filename for download
    file_size: int = 0
    wm_labels: list[str] = Field(default_factory=list)


class ProjectExportRunner(SimpleToolRunner):
    """Runner for project export."""

    async def _gather_metadata(
        self: Self,
        project_id: str,
        user_id: str,
    ) -> dict[str, Any]:
        """Gather all project metadata from PostgreSQL via asyncpg."""
        if self.settings is None:
            raise RuntimeError("Settings not initialized")

        schema = self.settings.customer_schema

        conn = await asyncpg.connect(
            host=self.settings.postgres_server,
            port=self.settings.postgres_port,
            user=self.settings.postgres_user,
            password=self.settings.postgres_password,
            database=self.settings.postgres_db,
        )

        try:
            # Set up JSON/JSONB codecs
            await conn.set_type_codec(
                "jsonb",
                encoder=json.dumps,
                decoder=json.loads,
                schema="pg_catalog",
            )
            await conn.set_type_codec(
                "json",
                encoder=json.dumps,
                decoder=json.loads,
                schema="pg_catalog",
            )

            project_uuid = uuid.UUID(project_id)
            user_uuid = uuid.UUID(user_id)

            # 1. Project record
            project_row = await conn.fetchrow(
                f"""
                SELECT id, user_id, name, description, basemap, custom_basemaps,
                       max_extent, builder_config, tags, thumbnail_url
                FROM {schema}.project
                WHERE id = $1
                """,
                project_uuid,
            )
            if project_row is None:
                raise ValueError(f"Project {project_id} not found")

            project_metadata: dict[str, Any] = {
                "id": str(project_row["id"]),
                "name": project_row["name"],
                "description": project_row["description"],
                "basemap": project_row["basemap"],
                "custom_basemaps": project_row["custom_basemaps"],
                "max_extent": project_row["max_extent"],
                "builder_config": project_row["builder_config"],
                "tags": project_row["tags"],
            }

            # 2. Thumbnail S3 key. A URL or a root-relative path (the artwork
            # the web app ships) is not in the bucket.
            thumbnail_s3_key: str | None = None
            thumb_url = project_row["thumbnail_url"]
            if thumb_url and not thumb_url.startswith(("http", "/")):
                thumbnail_s3_key = thumb_url

            # 3. UserProjectLink — initial_view_state. The exporter's own row
            # when they have one; otherwise the owner's, which is the view the
            # project actually opens to. Someone exporting a shared project they
            # never opened has no row at all, and the key is left out so the
            # importer applies its default rather than inserting NULL.
            owner_uuid: uuid.UUID | None = project_row["user_id"]
            view_candidates = [
                uid for uid in dict.fromkeys((user_uuid, owner_uuid)) if uid
            ]
            view_rows = await conn.fetch(
                f"""
                SELECT user_id, initial_view_state
                FROM {schema}.user_project
                WHERE project_id = $1 AND user_id = ANY($2::uuid[])
                """,
                project_uuid,
                view_candidates,
            )
            view_by_user = {
                row["user_id"]: row["initial_view_state"] for row in view_rows
            }
            initial_view_state = view_by_user.get(user_uuid) or view_by_user.get(
                owner_uuid
            )
            if initial_view_state:
                project_metadata["initial_view_state"] = initial_view_state

            # 4. LayerProjectLinks + Layer records
            lp_rows = await conn.fetch(
                f"""
                SELECT id, layer_id, project_id, layer_project_group_id,
                       "order", name, properties, other_properties, query, charts
                FROM {schema}.layer_project
                WHERE project_id = $1
                """,
                project_uuid,
            )

            # 4a. Workflows, read before the layers: the datasets they name
            # besides the project's layers travel with the project too
            wf_rows = await conn.fetch(
                f"""
                SELECT id, name, description, is_default, config, thumbnail_url
                FROM {schema}.workflow
                WHERE project_id = $1
                """,
                project_uuid,
            )
            workflows: list[dict[str, Any]] = [
                {
                    "id": str(row["id"]),
                    "name": row["name"],
                    "description": row["description"],
                    "is_default": row["is_default"],
                    "config": row["config"],
                    "thumbnail_url": row["thumbnail_url"],
                }
                for row in wf_rows
            ]

            # A workflow can name datasets that are not the project's layers
            # (picked from someone's own datasets). Those the exporter may read
            # are packed like the project's layers; catalog layers and public
            # datasets keep their id, as everyone may read them; any other is
            # removed from the archive, so no copy names someone else's data,
            # and its node asks for a dataset after the import.
            project_layer_ids = {str(row["layer_id"]) for row in lp_rows}
            named = (
                set().union(*(workflow_layer_refs(wf["config"]) for wf in workflows))
                - project_layer_ids
            )
            workflow_only_ids: list[uuid.UUID] = []
            if named:
                access_rows = await conn.fetch(
                    f"""
                    SELECT CAST(l AS text) AS id,
                           {schema}.layer_is_catalog(l)
                           OR EXISTS (
                               SELECT 1 FROM {schema}.layer x
                               WHERE x.id = l AND x.public_read
                           ) AS everyone_reads,
                           COALESCE({schema}.can('layer', l, $2, 'read'), FALSE)
                               AS readable
                    FROM unnest($1::uuid[]) AS l
                    """,
                    [uuid.UUID(layer_id) for layer_id in named],
                    user_uuid,
                )
                kept = {r["id"] for r in access_rows if r["everyone_reads"]}
                packed = {
                    r["id"]
                    for r in access_rows
                    if r["readable"] and not r["everyone_reads"]
                }
                unreadable = named - kept - packed
                if unreadable:
                    workflows = [
                        {**wf, "config": drop_layer_refs(wf["config"], unreadable)}
                        for wf in workflows
                    ]
                workflow_only_ids = [uuid.UUID(layer_id) for layer_id in packed]

            layer_ids: list[uuid.UUID] = [
                *(row["layer_id"] for row in lp_rows),
                *workflow_only_ids,
            ]

            # Fetch layers in batch
            layers_by_id: dict[str, dict[str, Any]] = {}
            layer_rows: list[Any] = []
            if layer_ids:
                layer_rows = await conn.fetch(
                    f"""
                    SELECT id, name, description, type, url,
                           data_type, feature_layer_type,
                           feature_layer_geometry_type, tool_type, job_id,
                           properties, other_properties, size,
                           thumbnail_url, tags, public_read,
                           user_id, folder_id, field_config
                    FROM {schema}.layer
                    WHERE id = ANY($1)
                    """,
                    layer_ids,
                )
                for row in layer_rows:
                    lid = str(row["id"])
                    layers_by_id[lid] = {
                        "id": lid,
                        "name": row["name"],
                        "description": row["description"],
                        "type": row["type"],
                        "url": row["url"],
                        "data_type": row["data_type"],
                        "feature_layer_type": row["feature_layer_type"],
                        "feature_layer_geometry_type": row[
                            "feature_layer_geometry_type"
                        ],
                        "tool_type": row["tool_type"],
                        "job_id": str(row["job_id"]) if row["job_id"] else None,
                        "properties": row["properties"],
                        "other_properties": row["other_properties"],
                        "size": row["size"],
                        "thumbnail_url": row["thumbnail_url"],
                        "tags": list(row["tags"]) if row["tags"] else None,
                        "public_read": row["public_read"],
                        "user_id": str(row["user_id"]) if row["user_id"] else None,
                        "folder_id": (
                            str(row["folder_id"]) if row["folder_id"] else None
                        ),
                        # Per-column metadata: formula/computed kinds and
                        # display config. Without it, imported layers keep
                        # the values but lose the definitions.
                        "field_config": row["field_config"] or {},
                    }

            # Exclude system layers (e.g. street_network) from export
            excluded_layer_ids: set[str] = set()
            for lid, layer_data in list(layers_by_id.items()):
                if layer_data.get("feature_layer_type") == "street_network":
                    excluded_layer_ids.add(lid)
                    del layers_by_id[lid]
                    logger.info(
                        "Excluding system layer from export: %s", layer_data.get("name")
                    )

            # Serialise layer_project_links as a list — multiple links may
            # reference the same layer_id (same dataset rendered with
            # different style/query), so a dict keyed by layer_id would
            # silently collapse them.
            layer_project_links_list: list[dict[str, Any]] = []
            for lp in lp_rows:
                if str(lp["layer_id"]) in excluded_layer_ids:
                    continue
                layer_project_links_list.append(
                    {
                        "id": lp["id"],
                        "layer_id": str(lp["layer_id"]),
                        "project_id": str(lp["project_id"]),
                        "layer_project_group_id": lp["layer_project_group_id"],
                        "order": lp["order"],
                        "name": lp["name"],
                        "properties": lp["properties"],
                        "other_properties": lp["other_properties"],
                        "query": lp["query"],
                        "charts": lp["charts"],
                    }
                )

            # 5. LayerProjectGroups
            group_rows = await conn.fetch(
                f"""
                SELECT id, name, "order", properties, project_id, parent_id
                FROM {schema}.layer_project_group
                WHERE project_id = $1
                """,
                project_uuid,
            )
            layer_groups: list[dict[str, Any]] = [
                {
                    "id": row["id"],
                    "name": row["name"],
                    "order": row["order"],
                    "properties": row["properties"],
                    "project_id": str(row["project_id"]),
                    "parent_id": row["parent_id"],
                }
                for row in group_rows
            ]

            # 7. ReportLayouts
            rpt_rows = await conn.fetch(
                f"""
                SELECT id, name, description, is_default, is_predefined,
                       config, thumbnail_url
                FROM {schema}.report_layout
                WHERE project_id = $1
                """,
                project_uuid,
            )
            reports: list[dict[str, Any]] = [
                {
                    "id": str(row["id"]),
                    "name": row["name"],
                    "description": row["description"],
                    "is_default": row["is_default"],
                    "is_predefined": row["is_predefined"],
                    "config": row["config"],
                    "thumbnail_url": row["thumbnail_url"],
                }
                for row in rpt_rows
            ]

            # 8. UploadedAssets — scan layer properties for S3 key references.
            # Icons and images are owned by whoever uploaded them: the exporter,
            # the project owner, or the owner of a layer in the project. All of
            # those are candidates; the reference scan below decides.
            asset_owner_ids = [
                uid
                for uid in dict.fromkeys(
                    (user_uuid, owner_uuid, *(row["user_id"] for row in layer_rows))
                )
                if uid
            ]
            asset_rows = await conn.fetch(
                f"""
                SELECT id, s3_key, file_name, display_name, category,
                       mime_type, file_size, asset_type, content_hash
                FROM {schema}.uploaded_asset
                WHERE user_id = ANY($1::uuid[])
                """,
                asset_owner_ids,
            )

            # Build a combined string from layer JSONB fields for searching
            searchable_parts: list[str] = []
            for layer in layers_by_id.values():
                for field_name in ("properties", "other_properties"):
                    field_val = layer.get(field_name)
                    if field_val is not None:
                        try:
                            searchable_parts.append(json.dumps(field_val))
                        except (TypeError, ValueError):
                            searchable_parts.append(str(field_val))
            combined_str = " ".join(searchable_parts)

            referenced_s3_keys: set[str] = set()
            for asset in asset_rows:
                if asset["s3_key"] in combined_str:
                    referenced_s3_keys.add(asset["s3_key"])

            matched_assets: list[dict[str, Any]] = []
            for asset in asset_rows:
                if asset["s3_key"] in referenced_s3_keys:
                    matched_assets.append(
                        {
                            "id": str(asset["id"]),
                            "s3_key": asset["s3_key"],
                            "file_name": asset["file_name"],
                            "display_name": asset["display_name"],
                            "category": asset["category"],
                            "mime_type": asset["mime_type"],
                            "file_size": asset["file_size"],
                            "asset_type": asset["asset_type"],
                            "content_hash": asset["content_hash"],
                        }
                    )

            asset_s3_keys: list[str] = list(referenced_s3_keys)

            return {
                "project_metadata": project_metadata,
                "layers": list(layers_by_id.values()),
                "layer_project_links": layer_project_links_list,
                "layer_groups": layer_groups,
                "workflows": workflows,
                "reports": reports,
                "assets": matched_assets,
                "asset_s3_keys": asset_s3_keys,
                "thumbnail_s3_key": thumbnail_s3_key,
            }

        finally:
            await conn.close()

    def _compute_sha256(self: Self, file_path: Path) -> str:
        """Compute SHA-256 hash of a file."""
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return f"sha256:{h.hexdigest()}"

    def _write_json(self: Self, data: Any, path: Path) -> None:
        """Write JSON data to a file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def _export_layer_data(
        self: Self,
        layer_id: str,
        owner_id: str,
        output_path: Path,
    ) -> int:
        """Export a single layer's data from DuckLake to GeoParquet.

        Returns row count.
        """
        from goatlib.io.parquet import write_optimized_parquet

        table_path = self.resolve_layer_table_path(layer_id)

        # Check table exists. DESCRIBE probes only this table;
        # information_schema.tables would lazily load every table in the
        # catalog to answer.
        try:
            self.duckdb_con.execute(f"DESCRIBE {quoted_relation(table_path)}")
        except duckdb.CatalogException:
            logger.warning("DuckLake table not found: %s", table_path)
            return 0

        # Check if table has geometry
        columns = self.duckdb_con.execute(
            f"DESCRIBE SELECT * FROM {table_path}"
        ).fetchall()
        has_geometry = any(col[1].upper() == "GEOMETRY" for col in columns)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        geometry_col = "geometry" if has_geometry else "__no_geometry__"

        row_count = write_optimized_parquet(
            con=self.duckdb_con,
            source=table_path,
            output_path=str(output_path),
            geometry_column=geometry_col,
        )

        logger.info(
            "Exported layer %s: %d rows to %s", layer_id, row_count, output_path
        )
        return row_count

    def _fetch_s3_asset(self: Self, s3_key: str, output_path: Path) -> bool:
        """Download an S3 object to a local file. Returns True on success."""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            self.s3_client.download_file(
                Bucket=self.settings.s3_bucket_name,
                Key=s3_key,
                Filename=str(output_path),
            )
            return True
        except Exception as e:
            logger.warning("Failed to fetch S3 asset %s: %s", s3_key, e)
            return False

    def run(self: Self, params: ProjectExportParams) -> dict:
        """Execute the project export."""
        if self.settings is None:
            raise RuntimeError("Settings not initialized. Call init_from_env() first.")

        if not params.project_id:
            raise ValueError("project_id is required for project export")

        wm_labels: list[str] = []
        if params.triggered_by_email:
            wm_labels.append(params.triggered_by_email)

        # 1. Gather metadata from PostgreSQL
        metadata = asyncio.run(self._gather_metadata(params.project_id, params.user_id))

        project_metadata: dict[str, Any] = metadata["project_metadata"]
        layers: list[dict[str, Any]] = metadata["layers"]
        layer_project_links: list[dict[str, Any]] = metadata["layer_project_links"]
        layer_groups: list[dict[str, Any]] = metadata["layer_groups"]
        workflows: list[dict[str, Any]] = metadata["workflows"]
        reports: list[dict[str, Any]] = metadata["reports"]
        assets: list[dict[str, Any]] = metadata["assets"]
        thumbnail_s3_key: str | None = metadata["thumbnail_s3_key"]

        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            archive_dir = tmp_dir / "archive"
            archive_dir.mkdir()

            checksums: dict[str, str] = {}

            # 2. Write project.json
            project_path = archive_dir / "project.json"
            self._write_json(project_metadata, project_path)

            # 3. Write layers
            layers_dir = archive_dir / "layers"
            internal_count = 0
            external_count = 0

            for layer in layers:
                layer_id = layer["id"]
                layer_dir = layers_dir / layer_id
                layer_dir.mkdir(parents=True, exist_ok=True)

                # metadata.json
                is_external = layer.get("data_type") in EXTERNAL_DATA_TYPES
                layer["is_external"] = is_external
                meta_path = layer_dir / "metadata.json"
                self._write_json(layer, meta_path)

                # data.parquet (internal layers only)
                if not is_external:
                    # `or`, not a dict default: the key is always present now,
                    # and it is None for an unowned catalog layer.
                    owner_id = layer.get("user_id") or params.user_id
                    data_path = layer_dir / "data.parquet"
                    row_count = self._export_layer_data(
                        layer_id=layer_id,
                        owner_id=owner_id,
                        output_path=data_path,
                    )
                    if row_count > 0:
                        checksums[f"layers/{layer_id}/data.parquet"] = (
                            self._compute_sha256(data_path)
                        )
                    internal_count += 1
                else:
                    external_count += 1

            # 4. Write layers/index.json
            index_path = layers_dir / "index.json"
            self._write_json({"layers": layers}, index_path)

            # 4b. Write layer_project_links.json (format 1.1 — list of links).
            # Excludes any link referencing a system layer that was filtered out
            # from `layers` (e.g. street_network).
            kept_layer_ids = {layer["id"] for layer in layers}
            kept_links = [
                lk for lk in layer_project_links if lk.get("layer_id") in kept_layer_ids
            ]
            links_path = archive_dir / "layer_project_links.json"
            self._write_json({"links": kept_links}, links_path)

            # 5. Write layer_groups.json
            groups_path = archive_dir / "layer_groups.json"
            self._write_json({"groups": layer_groups}, groups_path)

            # 6. Write workflows
            workflows_dir = archive_dir / "workflows"
            for wf in workflows:
                wf_path = workflows_dir / f"{wf['id']}.json"
                self._write_json(wf, wf_path)

            # 7. Write reports
            reports_dir = archive_dir / "reports"
            for rpt in reports:
                rpt_path = reports_dir / f"{rpt['id']}.json"
                self._write_json(rpt, rpt_path)

            # 8. Fetch S3 assets
            assets_dir = archive_dir / "assets"
            if thumbnail_s3_key:
                self._fetch_s3_asset(
                    thumbnail_s3_key,
                    assets_dir / "thumbnail.png",
                )
            for asset_entry in assets:
                s3_key = asset_entry.get("s3_key", "")
                archive_name = asset_entry.get("archive_path", "")
                if s3_key and archive_name:
                    self._fetch_s3_asset(s3_key, archive_dir / archive_name)

            # Write assets/index.json
            if assets:
                assets_index_path = assets_dir / "index.json"
                self._write_json({"assets": assets}, assets_index_path)

            # 9. Compute checksums for JSON files
            for json_file in archive_dir.rglob("*.json"):
                rel = json_file.relative_to(archive_dir)
                checksums[str(rel)] = self._compute_sha256(json_file)

            # 10. Write manifest.json
            project_name = project_metadata.get("name", "project")
            manifest = ExportManifest(
                format_version=FORMAT_VERSION,
                exported_at=datetime.now(timezone.utc),
                source_instance=params.source_instance,
                project_name=project_name,
                checksums=checksums,
                layer_count=len(layers),
                internal_layer_count=internal_count,
                external_layer_count=external_count,
                workflow_count=len(workflows),
                report_count=len(reports),
            )
            manifest_path = archive_dir / "manifest.json"
            self._write_json(manifest.model_dump(mode="json"), manifest_path)

            # 11. Assemble ZIP
            safe_name = "".join(
                c if c.isalnum() or c in "-_" else "_" for c in project_name
            )
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            zip_name = f"project-export-{safe_name}-{timestamp}.zip"
            zip_path = tmp_dir / zip_name

            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for file_path in sorted(archive_dir.rglob("*")):
                    if file_path.is_file():
                        arcname = str(file_path.relative_to(archive_dir))
                        zf.write(file_path, arcname)

            file_size = zip_path.stat().st_size
            logger.info("ZIP assembled: %s (%d bytes)", zip_name, file_size)

            # 12. Upload ZIP to S3
            s3_key = f"exports/{params.user_id}/{zip_name}"
            with open(zip_path, "rb") as f:
                self.s3_client.put_object(
                    Bucket=self.settings.s3_bucket_name,
                    Key=s3_key,
                    Body=f,
                    ContentType="application/zip",
                )

            # 13. Generate presigned URL
            presigned_url = self.s3_public_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.settings.s3_bucket_name,
                    "Key": s3_key,
                },
                ExpiresIn=86400,  # 24 hours
            )

            output = ProjectExportOutput(
                s3_key=s3_key,
                presigned_url=presigned_url,
                download_url=presigned_url,
                file_name=zip_name,
                file_size=file_size,
                wm_labels=wm_labels,
            )
            return output.model_dump()


def main(params: ProjectExportParams) -> dict:
    """Windmill entry point for project export."""
    runner = ProjectExportRunner()
    runner.init_from_env()
    try:
        return runner.run(params)
    finally:
        runner.cleanup()
