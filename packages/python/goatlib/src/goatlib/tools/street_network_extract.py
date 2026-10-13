"""Create a street network bundle from GOAT's own routing network, for an area.

The routing network is the hive-partitioned edges/nodes parquet the routing
tools read by default (``street_network_*_base_path``). This cuts it to an area
and stores the result as a street_network bundle with its routable artifact, the
same kind of bundle an import or a filtered copy produces.

The layers follow the Overture importer's schema column for column, ids as
text, so the bundle is the same as any other street network. Nodes are taken as
the endpoints of the kept edges rather than clipped on their
own, so no kept edge loses a node. The artifact is built by the standard builder,
which routes flat: the network's slope impedances are not carried over.
"""

import glob
import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

import duckdb
from pydantic import ConfigDict, Field

from goatlib.analysis.schemas.ui import (
    SECTION_INPUT,
    SECTION_OUTPUT,
    ui_field,
    ui_sections,
)
from goatlib.bundles.runner import BundleImportRunner, ImportedLayer
from goatlib.io.parquet import write_optimized_parquet
from goatlib.models.bundle import (
    BundleStatus,
    BundleTypeName,
    get_spec,
    role_field_config,
)
from goatlib.models.io import DatasetMetadata
from goatlib.tasks.sync_base_data import h3_3_cells_for_bbox
from goatlib.tools.authz import require_can
from goatlib.tools.data_integration import area_envelope, area_table
from goatlib.tools.db import ToolDatabaseService, normalize_geometry_type
from goatlib.tools.schemas import ToolInputBase
from goatlib.tools.style import get_bundle_style

logger = logging.getLogger(__name__)

#: Above this the extract fails rather than building a graph cut at an arbitrary edge.
MAX_EDGES = 2_000_000


class StreetNetworkExtractParams(ToolInputBase):
    """Where to cut the routing network, and where the bundle goes."""

    model_config = ConfigDict(
        json_schema_extra=ui_sections(SECTION_INPUT, SECTION_OUTPUT)
    )

    area: dict = Field(
        ...,
        description="GeoJSON polygon the network is cut to",
        json_schema_extra=ui_field(section="input", field_order=1, hidden=True),
    )
    classes: Optional[List[str]] = Field(
        None,
        description="Road classes to keep, e.g. primary or footway; all when empty",
        json_schema_extra=ui_field(section="input", field_order=2),
    )
    folder_id: str = Field(
        ...,
        description="Folder the bundle and its layers are created in",
        json_schema_extra=ui_field(section="output", field_order=1, hidden=True),
    )
    result_bundle_name: Optional[str] = Field(
        None,
        description="Name for the new bundle",
        json_schema_extra=ui_field(section="output", field_order=3),
    )
    project_id: Optional[str] = Field(
        None,
        description="Add the new bundle to this project once its layers exist",
        json_schema_extra=ui_field(section="output", field_order=2, hidden=True),
    )


def _quote(value: str) -> str:
    return value.replace("'", "''")


def _partition_files(base: str, cells: set[int]) -> list[str]:
    return sorted(
        f
        for cell in cells
        for f in glob.glob(os.path.join(base, f"h3_3={cell}", "*.parquet"))
    )


def export_network(
    con: "duckdb.DuckDBPyConnection",
    *,
    area: dict,
    classes: Optional[List[str]],
    edges_base: str,
    nodes_base: str,
    workdir: str,
) -> dict[str, str]:
    """Write the area's edges and nodes in the street_network role contract."""
    con.execute("INSTALL spatial; LOAD spatial;")
    envelope = area_envelope(con, area_table(con, area))
    # One ring around the area's cells: an edge is filed under one cell but can
    # reach into the next, and so can the node at its far end.
    cells = h3_3_cells_for_bbox(list(envelope), ring=1)
    edge_files = _partition_files(edges_base, cells)
    node_files = _partition_files(nodes_base, cells)
    if not edge_files or not node_files:
        raise ValueError("The GOAT routing network does not cover this area.")

    x0, y0, x1, y1 = con.execute(
        """SELECT ST_XMin(e), ST_YMin(e), ST_XMax(e), ST_YMax(e) FROM (
             SELECT ST_Extent(ST_Transform(geom, 'EPSG:4326', 'EPSG:3857',
                                           always_xy := true)) AS e
             FROM fetch_area)"""
    ).fetchone()
    class_filter = (
        "class_ IN (" + ", ".join(f"'{_quote(c)}'" for c in classes) + ")"
        if classes
        else "TRUE"
    )
    edge_list = ", ".join(f"'{_quote(f)}'" for f in edge_files)
    node_list = ", ".join(f"'{_quote(f)}'" for f in node_files)

    # The coordinates' own box first, which is arithmetic; the line is only
    # built and tested against the area for edges that can reach it.
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE network_edges AS
        WITH near AS (
            SELECT * FROM read_parquet([{edge_list}], hive_partitioning = false)
            WHERE {class_filter}
              AND list_min(list_transform(coordinates_3857, c -> c[1])) <= {x1}
              AND list_max(list_transform(coordinates_3857, c -> c[1])) >= {x0}
              AND list_min(list_transform(coordinates_3857, c -> c[2])) <= {y1}
              AND list_max(list_transform(coordinates_3857, c -> c[2])) >= {y0}
        ), lines AS (
            SELECT *, ST_Transform(
                ST_MakeLine(list_transform(coordinates_3857, c -> ST_Point(c[1], c[2]))),
                'EPSG:3857', 'EPSG:4326', always_xy := true) AS geometry
            FROM near
        )
        SELECT
            CAST(l.id AS VARCHAR) AS id,
            CAST(NULL AS VARCHAR) AS name,
            l.class_ AS class,
            CAST(NULL AS VARCHAR) AS subclass,
            l.length_m,
            CAST(NULL AS VARCHAR) AS surface,
            CAST(l.maxspeed_forward AS INTEGER) AS speed_limit_kph_forward,
            CAST(l.maxspeed_backward AS INTEGER) AS speed_limit_kph_backward,
            CAST(l.source AS VARCHAR) AS source_node,
            CAST(l.target AS VARCHAR) AS target_node,
            CAST(NULL AS VARCHAR) AS other,
            CAST(NULL AS VARCHAR) AS original_id,
            l.geometry
        FROM lines l, fetch_area a
        WHERE ST_Intersects(l.geometry, a.geom)
        QUALIFY row_number() OVER (PARTITION BY l.id ORDER BY l.id) = 1
    """)
    count = con.execute("SELECT count(*) FROM network_edges").fetchone()[0]
    if not count:
        raise ValueError("The GOAT routing network has no streets in this area.")
    if count > MAX_EDGES:
        raise ValueError(
            f"The area holds more than {MAX_EDGES:,} street segments. "
            "Pick a smaller area or fewer road classes."
        )

    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE network_nodes AS
        SELECT CAST(id AS VARCHAR) AS id,
               ST_Transform(ST_Point(x_3857, y_3857), 'EPSG:3857', 'EPSG:4326',
                            always_xy := true) AS geometry
        FROM read_parquet([{node_list}], hive_partitioning = false)
        WHERE CAST(id AS VARCHAR) IN (
            SELECT source_node FROM network_edges
            UNION SELECT target_node FROM network_edges)
        QUALIFY row_number() OVER (PARTITION BY id ORDER BY id) = 1
    """)

    paths = {}
    for role, table in (("edges", "network_edges"), ("nodes", "network_nodes")):
        path = os.path.join(workdir, f"{role}.parquet")
        write_optimized_parquet(con, table, path, geometry_column="geometry")
        paths[role] = path
    logger.info(
        "cut %d edge(s) from the routing network (%d cell(s))", count, len(cells)
    )
    return paths


class StreetNetworkExtractRunner(BundleImportRunner):
    """Cuts the routing network to an area and stores it as a bundle."""

    def process(self, params: Any, temp_dir: Path) -> "tuple[Path, DatasetMetadata]":
        raise NotImplementedError(
            "StreetNetworkExtractRunner builds a bundle through run_extract()."
        )

    async def run_extract(
        self,
        *,
        area: dict,
        classes: Optional[List[str]],
        user_id: str,
        folder_id: str,
        result_bundle_name: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        assert self.settings is not None, "init_from_env()/init() must run first"
        pool = await self.get_postgres_pool()
        db = ToolDatabaseService(pool, schema=self.settings.customer_schema)
        try:
            # The job is dispatched without its inputs being checked, so the
            # folder is asked about here, before anything is created.
            await require_can(
                db,
                resource_type="folder",
                resource_id=folder_id,
                user_id=user_id,
                action="write",
                refusal=(
                    f"You cannot create content in folder {folder_id}, so the "
                    "street network has nowhere to go."
                ),
            )
            bundle_type = BundleTypeName.street_network
            spec = get_spec(bundle_type)
            name = result_bundle_name or "GOAT street network"
            bundle_id = str(uuid4())
            await db.create_bundle(
                bundle_id=bundle_id,
                user_id=user_id,
                folder_id=folder_id,
                name=name,
                bundle_type=bundle_type,
                status=BundleStatus.processing,
                dataset_metadata={
                    "lineage": "Cut from the GOAT routing network (Overture "
                    "transportation, processed by goat-data)",
                    "license": "ODbL-1.0",
                    "attribution": "© OpenStreetMap contributors, Overture Maps "
                    "Foundation",
                    "distributor_name": "Overture Maps Foundation",
                },
            )

            imported: List[ImportedLayer] = []
            try:
                with tempfile.TemporaryDirectory(prefix="goat_network_cut_") as workdir:
                    con = duckdb.connect()
                    try:
                        paths = export_network(
                            con,
                            area=area,
                            classes=classes,
                            edges_base=self.settings.street_network_edges_base_path,
                            nodes_base=self.settings.street_network_nodes_base_path,
                            workdir=workdir,
                        )
                    finally:
                        con.close()
                    for role, path in paths.items():
                        imported.append(
                            await self._store_member(
                                db,
                                role=role,
                                path=path,
                                user_id=user_id,
                                folder_id=folder_id,
                                bundle_id=bundle_id,
                                bundle_name=name,
                                spec=spec,
                            )
                        )
                await self.build_and_store_artifacts(
                    db,
                    bundle_id=bundle_id,
                    bundle_type=bundle_type,
                    source_path="",
                    user_id=user_id,
                    members=[
                        {"role": layer.role, "layer_id": layer.layer_id}
                        for layer in imported
                    ],
                )
            except Exception:
                await self._rollback_bundle(
                    db, user_id=user_id, bundle_id=bundle_id, imported=imported
                )
                raise

            await db.update_bundle_status(
                bundle_id=bundle_id, status=BundleStatus.ready
            )
            if project_id:
                try:
                    await self._add_bundle_to_project(
                        db,
                        project_id=project_id,
                        bundle_id=bundle_id,
                        bundle_type=bundle_type,
                        imported=imported,
                    )
                except Exception as e:  # noqa: BLE001 - the bundle matters more
                    logger.warning(
                        "Street network %s created but not added to project %s: %s",
                        bundle_id,
                        project_id,
                        e,
                    )
            return {
                "bundle_id": bundle_id,
                "bundle_type": bundle_type.value,
                "layers": [layer.model_dump() for layer in imported],
            }
        finally:
            await pool.close()
            self.cleanup()

    async def _store_member(
        self,
        db: ToolDatabaseService,
        *,
        role: str,
        path: str,
        user_id: str,
        folder_id: str,
        bundle_id: str,
        bundle_name: str,
        spec: Any,
    ) -> ImportedLayer:
        """One written member as a layer of the bundle."""
        layer_id = str(uuid4())
        info = self._ingest_to_ducklake(
            user_id=user_id, layer_id=layer_id, parquet_path=Path(path)
        )
        geometry_type = normalize_geometry_type(info.get("geometry_type"))
        role_spec = spec.role(role)
        await db.create_layer(
            layer_id=layer_id,
            user_id=user_id,
            folder_id=folder_id,
            name=f"{bundle_name} {role_spec.label if role_spec else role}",
            layer_type="feature",
            feature_layer_type="standard",
            geometry_type=geometry_type,
            extent_wkt=info.get("extent_wkt"),
            feature_count=info.get("feature_count", 0),
            size=info.get("size", 0),
            properties=get_bundle_style(spec.type, role, geometry_type)
            if geometry_type
            else None,
        )
        field_config = role_field_config(role_spec)
        if field_config:
            await db.set_layer_field_config(layer_id, field_config)
        await db.add_layer_to_bundle(bundle_id=bundle_id, layer_id=layer_id, role=role)
        return ImportedLayer(
            role=role,
            layer_id=layer_id,
            name=role,
            layer_type="feature",
            geometry_type=geometry_type,
            feature_count=info.get("feature_count", 0),
        )


def main(params: StreetNetworkExtractParams) -> dict:
    """Windmill entry point."""
    from goatlib.tools.base import _get_or_create_event_loop

    runner = StreetNetworkExtractRunner()
    runner.init_from_env()
    return _get_or_create_event_loop().run_until_complete(
        runner.run_extract(
            area=params.area,
            classes=params.classes,
            user_id=params.user_id,
            folder_id=params.folder_id,
            result_bundle_name=params.result_bundle_name,
            project_id=params.project_id,
        )
    )
