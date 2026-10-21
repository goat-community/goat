import logging
from pathlib import Path
from typing import Any, List, Optional, Self, Tuple

from goatlib.analysis.core.base import AnalysisTool
from goatlib.analysis.schemas.geoprocessing import UnionParams
from goatlib.io.parquet import write_optimized_parquet
from goatlib.models.io import DatasetMetadata

logger = logging.getLogger(__name__)


class UnionTool(AnalysisTool):
    """
    UnionTool: Combines layers with topological splitting at intersections
    (equivalent to QGIS union/vereinigen).
    Creates separate features for overlapping and non-overlapping parts.
    """

    def _run_implementation(
        self: Self, params: UnionParams
    ) -> List[Tuple[Path, DatasetMetadata]]:
        """Perform union operation on vector datasets."""

        # Import input dataset
        input_meta, input_table = self.import_input(params.input_path, "input")

        # Import overlay dataset if provided, otherwise perform self-union
        overlay_meta = None
        overlay_table = None
        if params.overlay_path:
            overlay_meta, overlay_table = self.import_input(
                params.overlay_path, "overlay"
            )

        # Validate geometry columns
        input_geom = input_meta.geometry_column
        if not input_geom:
            raise ValueError("The input layer has no geometry column.")

        overlay_geom = None
        if overlay_meta:
            overlay_geom = overlay_meta.geometry_column
            if not overlay_geom:
                raise ValueError("The overlay layer has no geometry column.")

        # Validate geometry types
        self.validate_geometry_types(
            input_table, input_geom, params.accepted_input_geometry_types, "input"
        )
        if overlay_meta and overlay_table and overlay_geom:
            self.validate_geometry_types(
                overlay_table,
                overlay_geom,
                params.accepted_overlay_geometry_types,
                "overlay",
            )

        # Get CRS from input metadata, fallback to output_crs or EPSG:4326
        input_crs = input_meta.crs
        if input_crs:
            input_crs_str = input_crs.to_string()
        else:
            input_crs_str = params.output_crs or "EPSG:4326"
            logger.warning(
                "Could not detect CRS for %s, using fallback: %s",
                params.input_path,
                input_crs_str,
            )

        overlay_crs_str = None
        if overlay_meta:
            overlay_crs = overlay_meta.crs
            if overlay_crs:
                overlay_crs_str = overlay_crs.to_string()
            else:
                overlay_crs_str = params.output_crs or "EPSG:4326"
                logger.warning(
                    "Could not detect CRS for %s, using fallback: %s",
                    params.overlay_path,
                    overlay_crs_str,
                )

            # Validate CRS compatibility
            if input_crs_str != overlay_crs_str:
                logger.info(
                    "CRS mismatch detected. Input: %s, Overlay: %s",
                    input_crs_str,
                    overlay_crs_str,
                )
                logger.info("Transforming overlay layer to match input CRS")

        # Define output path
        if not params.output_path:
            suffix = "_self_union" if not params.overlay_path else "_union"
            params.output_path = str(
                Path(params.input_path).parent
                / f"{Path(params.input_path).stem}{suffix}.parquet"
            )
        output_path = Path(params.output_path)

        logger.info(
            "Starting union: input='%s' | overlay='%s' | input_geom='%s' | overlay_geom='%s'",
            params.input_path,
            params.overlay_path or "None (self-union)",
            input_geom,
            overlay_geom or "N/A",
        )

        # Execute union operation
        self._execute_union(
            params,
            input_table,
            overlay_table,
            input_meta,
            overlay_meta,
            input_geom,
            overlay_geom,
            input_crs_str,
            overlay_crs_str,
            output_path,
        )

        # Determine output geometry type (same as input)
        output_geometry_type = input_meta.geometry_type

        metadata = DatasetMetadata(
            path=str(output_path),
            source_type="vector",
            format="geoparquet",
            crs=params.output_crs or input_crs_str,
            geometry_type=output_geometry_type,
        )

        logger.info("Union completed successfully → %s", output_path)
        return [(output_path, metadata)]

    def _execute_union(
        self: Self,
        params: UnionParams,
        input_table: str,
        overlay_table: Optional[str],
        input_meta: Any,
        overlay_meta: Optional[Any],
        input_geom: str,
        overlay_geom: Optional[str],
        input_crs: Optional[str],
        overlay_crs: Optional[str],
        output_path: Path,
    ) -> None:
        """Execute the union operation in DuckDB."""

        if overlay_table is None:
            # Self-union: split overlapping features within the same layer
            self._execute_self_union(
                params, input_table, input_geom, input_crs, output_path
            )
        else:
            # Two-layer union: combine features from both layers
            self._execute_two_layer_union(
                params,
                input_table,
                overlay_table,
                input_meta,
                overlay_meta,
                input_geom,
                overlay_geom,
                input_crs,
                overlay_crs,
                output_path,
            )

    def _execute_self_union(
        self: Self,
        params: UnionParams,
        input_table: str,
        input_geom: str,
        input_crs: Optional[str],
        output_path: Path,
    ) -> None:
        """Execute self-union operation to split overlapping features within the layer."""
        logger.info("Performing self-union (dissolve) operation")

        # Self-union dissolves all geometries into a single unified geometry
        # Then explode it back into individual features using UNNEST(ST_Dump(...))
        self.con.execute(f"""
            CREATE OR REPLACE VIEW unioned AS
            SELECT
                ROW_NUMBER() OVER () AS fid,
                geom_part.geom AS {input_geom}
            FROM (
                SELECT UNNEST(ST_Dump(ST_Union_Agg({input_geom}))) as geom_part
                FROM {input_table}
                WHERE ST_IsValid({input_geom})
            )
        """)

        # Handle output CRS transformation if needed
        output_view = "unioned"
        if params.output_crs and input_crs and params.output_crs != input_crs:
            self.con.execute(f"""
                CREATE OR REPLACE VIEW unioned_transformed AS
                SELECT fid,
                    ST_Transform({input_geom}, '{input_crs}', '{params.output_crs}') AS {input_geom}
                FROM unioned
            """)
            output_view = "unioned_transformed"

        # Export to file
        write_optimized_parquet(
            self.con,
            output_view,
            output_path,
            geometry_column=input_geom,
        )

        logger.info("Self-union data written to %s", output_path)

    def _execute_two_layer_union(
        self: Self,
        params: UnionParams,
        input_table: str,
        overlay_table: str,
        input_meta: Any,
        overlay_meta: Any,
        input_geom: str,
        overlay_geom: str,
        input_crs: Optional[str],
        overlay_crs: Optional[str],
        output_path: Path,
    ) -> None:
        """Execute two-layer union operation using QGIS-style algorithm.

        Splits features from each layer at their overlap with features from the other layer.
        Overlapping areas appear multiple times (once per participating feature from each layer).
        """
        logger.info("Performing QGIS-style two-layer union with bbox spatial filtering")

        # For WGS84 datasets, assume both are in EPSG:4326 (no CRS conversion needed)
        logger.info(
            "Assuming both datasets are in EPSG:4326 (WGS84) - no CRS conversion required"
        )

        # Determine allowed output geometry types to filter degenerate geometries
        allowed_types = self.get_allowed_output_geometry_types(input_table, input_geom)
        logger.info(
            f"Filtering output to geometry types: {allowed_types or 'all types'}"
        )

        # Build geometry type filter clause
        geom_type_filter = (
            f"AND ST_GeometryType({input_geom}) IN {allowed_types}"
            if allowed_types
            else ""
        )

        # Attribute columns of each side; either may have none (a dissolve
        # without group fields writes a geometry alone). Each of the three
        # parts below lists the same columns in the same order, NULL where its
        # side is missing, so UNION ALL lines them up.
        input_cols = self._attribute_columns(input_table, input_geom)
        overlay_cols = self._attribute_columns(overlay_table, overlay_geom)
        prefix = params.overlay_fields_prefix or ""
        input_fields = [f'i."{col}"' for col in input_cols]
        null_input_fields = [f'NULL AS "{col}"' for col in input_cols]
        overlay_fields = [f'o."{col}" AS "{prefix}{col}"' for col in overlay_cols]
        null_overlay_fields = [f'NULL AS "{prefix}{col}"' for col in overlay_cols]
        overlap_select = _select_list(
            input_fields,
            overlay_fields,
            f"ST_Intersection(i.{input_geom}, o.{overlay_geom}) AS {input_geom}",
        )
        input_only_select = _select_list(
            input_fields,
            null_overlay_fields,
            f"ST_Difference(i.{input_geom}, u.geom) AS {input_geom}",
        )
        overlay_only_select = _select_list(
            null_input_fields,
            overlay_fields,
            f"ST_Difference(o.{overlay_geom}, u.geom) AS {input_geom}",
        )

        # Create unified geometries for difference operations
        logger.info("Creating unified geometries for difference operations")
        self.con.execute(f"""
            CREATE OR REPLACE TABLE unified_overlay AS
            SELECT ST_Union_Agg({overlay_geom}) as geom
            FROM {overlay_table}
            WHERE ST_IsValid({overlay_geom})
        """)

        self.con.execute(f"""
            CREATE OR REPLACE TABLE unified_input AS
            SELECT ST_Union_Agg({input_geom}) as geom
            FROM {input_table}
            WHERE ST_IsValid({input_geom})
        """)

        # Part 1: Overlapping features with attributes from BOTH layers
        logger.info("Creating overlapping features with attributes from both layers")
        self.con.execute(f"""
            CREATE OR REPLACE VIEW overlapping_features AS
            SELECT
                {overlap_select}
            FROM {input_table} i
            INNER JOIN {overlay_table} o ON ST_Intersects(i.{input_geom}, o.{overlay_geom})
            WHERE ST_IsValid(i.{input_geom})
                AND ST_IsValid(o.{overlay_geom})
                AND NOT ST_IsEmpty(ST_Intersection(i.{input_geom}, o.{overlay_geom}))
                {geom_type_filter.replace(input_geom, f"ST_Intersection(i.{input_geom}, o.{overlay_geom})")}
        """)

        # Part 2: Input-only features (subtract overlay from each input feature)
        logger.info("Creating input-only features")
        self.con.execute(f"""
            CREATE OR REPLACE VIEW input_only AS
            SELECT
                {input_only_select}
            FROM {input_table} i
            CROSS JOIN unified_overlay u
            WHERE ST_IsValid(i.{input_geom})
                AND NOT ST_IsEmpty(ST_Difference(i.{input_geom}, u.geom))
                {geom_type_filter.replace(input_geom, f"ST_Difference(i.{input_geom}, u.geom)")}
        """)

        # Part 3: Overlay-only features (subtract input from each overlay feature)
        logger.info("Creating overlay-only features")
        self.con.execute(f"""
            CREATE OR REPLACE VIEW overlay_only AS
            SELECT
                {overlay_only_select}
            FROM {overlay_table} o
            CROSS JOIN unified_input u
            WHERE ST_IsValid(o.{overlay_geom})
                AND NOT ST_IsEmpty(ST_Difference(o.{overlay_geom}, u.geom))
                {geom_type_filter.replace(input_geom, f"ST_Difference(o.{overlay_geom}, u.geom)")}
        """)

        # Combine all parts
        logger.info("Combining all union parts")
        self.con.execute("""
            CREATE OR REPLACE VIEW unioned AS
            SELECT * FROM overlapping_features
            UNION ALL
            SELECT * FROM input_only
            UNION ALL
            SELECT * FROM overlay_only
        """)

        # Handle output CRS transformation if needed
        output_view = "unioned"
        if params.output_crs and input_crs and params.output_crs != input_crs:
            self.con.execute(f"""
                CREATE OR REPLACE VIEW unioned_transformed AS
                SELECT * EXCLUDE ({input_geom}),
                    ST_Transform({input_geom}, '{input_crs}', '{params.output_crs}') AS {input_geom}
                FROM unioned
            """)
            output_view = "unioned_transformed"

        # Export to file
        write_optimized_parquet(
            self.con,
            output_view,
            output_path,
            geometry_column=input_geom,
        )

        logger.info("Two-layer union data written to %s", output_path)

    def _attribute_columns(self: Self, table_name: str, geom_column: str) -> list[str]:
        """Every column of the table but the geometry and the bbox."""
        rows = self.con.execute(f"DESCRIBE {table_name}").fetchall()
        return [row[0] for row in rows if row[0] not in (geom_column, "bbox")]


def _select_list(*parts: list[str] | str) -> str:
    """A select list of the given column expressions, empty lists skipped."""
    columns = [
        column
        for part in parts
        for column in ([part] if isinstance(part, str) else part)
    ]
    return ",\n                ".join(columns)
