"""Layer create tool for Windmill.

Creates empty layers (with or without geometry) in DuckLake storage.
Users define a layer name, optional geometry type, and custom field definitions.
"""

import json
import logging
from pathlib import Path
from typing import Any, Literal, Self

import pyarrow as pa
import pyarrow.parquet as pq
from pydantic import BaseModel, Field, model_validator

from goatlib.models.io import DatasetMetadata
from goatlib.tools.base import (
    BaseToolRunner,
    _get_or_create_event_loop,
    drops_unrecorded_tables,
)
from goatlib.tools.schemas import ToolInputBase
from goatlib.utils.field_config import coerce_allowed_values
from goatlib.utils.generated_fields import generated_entry_settings, is_generated_kind

logger = logging.getLogger(__name__)

# Map user-facing geometry types to GeoJSON/WKB geometry type names
GEOMETRY_TYPE_MAP: dict[str, str] = {
    "point": "Point",
    "line": "LineString",
    "polygon": "Polygon",
}

# Storage type per field kind, matching what geoapi's `_resolve_kind_to_sql` gives a
# column added to an existing layer: string→VARCHAR, number→DOUBLE,
# datetime→TIMESTAMPTZ, boolean→BOOLEAN, serial→BIGINT, uuid→VARCHAR. Creation
# used to know only the first two, so a datetime field became text and a boolean
# the strings "true"/"false".
FIELD_TYPE_MAP: dict[str, pa.DataType] = {
    "string": pa.string(),
    "number": pa.float64(),
    "datetime": pa.timestamp("us", tz="UTC"),
    "boolean": pa.bool_(),
    "serial": pa.int64(),
    "uuid": pa.string(),
}

#: Kinds a new layer can carry. Computed kinds (area/perimeter/length) and formula
#: are deliberately absent: they need the compute SQL geoapi builds when a column is
#: added to a layer that already exists, which creation does not run — the column
#: would be created and never filled. The generated kinds (serial, uuid) need no
#: such step: the layer starts empty, and geoapi assigns a value to every feature
#: created in it (``goatlib.utils.generated_fields``).
FieldKind = Literal["string", "number", "datetime", "boolean", "serial", "uuid"]


class FieldDefinition(BaseModel):
    """Definition of a single field (column) for the new layer."""

    name: str = Field(..., description="Column name")
    kind: FieldKind | None = Field(
        None,
        description="Field kind, as used everywhere else in GOAT",
    )
    type: Literal["string", "number"] | None = Field(
        None,
        description="Legacy alias for `kind`, kept for callers that predate it",
    )
    allowed_values: list[Any] | None = Field(
        None,
        description="The only values this column may hold, if it is constrained",
    )
    allow_other: bool = Field(
        False,
        description="Treat allowed_values as suggestions rather than the only "
        "values a write may set",
    )
    start: int | None = Field(
        None,
        description="First number of a serial field (default 1). Only for "
        "kind='serial'.",
    )

    @property
    def storage_kind(self: Self) -> str:
        """The kind to store as, preferring `kind` and falling back to `type`."""
        return self.kind or self.type or "string"

    @model_validator(mode="after")
    def _coerce_vocabulary(self: Self) -> Self:
        """A number column's vocabulary has to be numbers.

        Coerced while the parameters are being parsed, so a feed of the wrong
        type fails before the layer exists rather than after — the entry is
        written once the layer is there, and a failure then leaves a real
        column the user cannot correct from the create dialog.
        """
        if is_generated_kind(self.storage_kind):
            if self.allowed_values:
                raise ValueError(
                    f"'{self.name}' is filled automatically, so it cannot have "
                    "allowed values."
                )
            # Raises for a start on a uuid field or a start that is no
            # whole number, before the layer exists.
            generated_entry_settings(self.storage_kind, self.start)
        elif self.start is not None:
            raise ValueError(f"Only a serial field has a start value ('{self.name}').")
        if self.allowed_values:
            self.allowed_values = coerce_allowed_values(
                self.storage_kind, self.allowed_values
            )
        return self

    def field_config_entry(self: Self) -> dict[str, Any]:
        """What `field_config` records about this column.

        The same shape geoapi writes when a column is added to an existing
        layer, so a column means the same thing however it got there.
        """
        entry: dict[str, Any] = {
            "kind": self.storage_kind,
            "is_computed": False,
            "depends_on": [],
            "display_config": {},
        }
        if is_generated_kind(self.storage_kind):
            entry.update(generated_entry_settings(self.storage_kind, self.start))
        if self.allowed_values:
            entry["allowed_values"] = self.allowed_values
            entry["allow_other"] = self.allow_other
        return entry


class LayerCreateParams(ToolInputBase):
    """Parameters for layer create tool."""

    name: str = Field(..., description="Layer name")
    geometry_type: Literal["point", "line", "polygon"] | None = Field(
        None,
        description="Geometry type for the layer. None creates a table without geometry.",
    )
    fields: list[FieldDefinition] = Field(
        default_factory=list,
        description="Field definitions for the layer",
    )
    description: str | None = Field(
        None,
        description="Layer description",
    )
    tags: list[str] | None = Field(
        None,
        description="Tags for categorizing the layer",
    )


class LayerCreateToolRunner(BaseToolRunner[LayerCreateParams]):
    """Layer create tool runner for Windmill.

    Creates empty layers with user-defined schema.
    Produces GeoParquet for geometry layers or plain Parquet for tables.
    """

    tool_class = None  # No analysis tool - we create layers directly
    output_geometry_type = None  # Determined at runtime from params
    default_output_name = "New Layer"

    def get_feature_layer_type(self: Self, params: LayerCreateParams) -> str:
        """Return 'standard' for user-created layers.

        Args:
            params: Create parameters

        Returns:
            "standard" for user-created layers
        """
        return "standard"

    def process(
        self: Self, params: LayerCreateParams, temp_dir: Path
    ) -> tuple[Path, DatasetMetadata]:
        """Create an empty Parquet file with the specified schema.

        For geometry layers: creates GeoParquet via geopandas with an empty
        GeoSeries in the specified CRS.
        For table layers: creates plain Parquet via pyarrow.

        Args:
            params: Layer create parameters
            temp_dir: Temporary directory for output file

        Returns:
            Tuple of (output_parquet_path, metadata)
        """
        output_path = temp_dir / "output.parquet"

        # Build PyArrow fields for user-defined columns
        pa_fields = [
            pa.field(f.name, FIELD_TYPE_MAP[f.storage_kind]) for f in params.fields
        ]

        geometry_type_name: str | None = None

        if params.geometry_type is not None:
            # Geometry layer: build GeoParquet directly via PyArrow.
            # Using geopandas with empty DataFrames loses column types
            # (empty lists default to float64), so we construct the
            # Arrow table with an explicit schema instead.
            geometry_type_name = GEOMETRY_TYPE_MAP[params.geometry_type]

            # Build an empty Arrow table with the user fields + geometry
            geo_field = pa.field(
                "geometry",
                pa.binary(),
                metadata={
                    b"ARROW:extension:name": b"geoarrow.wkb",
                    b"ARROW:extension:metadata": b'{"crs":{"type":"GeographicCRS","name":"WGS 84","datum":{"type":"GeodeticReferenceFrame","name":"World Geodetic System 1984","ellipsoid":{"name":"WGS 84","semi_major_axis":6378137,"inverse_flattening":298.257223563}},"coordinate_system":{"type":"ellipsoidal","axis":[{"name":"Geodetic latitude","abbreviation":"Lat","direction":"north","unit":"degree"},{"name":"Geodetic longitude","abbreviation":"Lon","direction":"east","unit":"degree"}]},"id":{"authority":"EPSG","code":4326}}}',
                },
            )
            full_schema = pa.schema(pa_fields + [geo_field])
            # Add GeoParquet metadata
            geo_metadata = {
                "version": "1.1.0",
                "primary_column": "geometry",
                "columns": {
                    "geometry": {
                        "encoding": "WKB",
                        "geometry_types": [geometry_type_name],
                        "crs": None,  # CRS is in the Arrow extension metadata
                    }
                },
            }
            existing_meta = full_schema.metadata or {}
            existing_meta[b"geo"] = json.dumps(geo_metadata).encode()
            full_schema = full_schema.with_metadata(existing_meta)

            empty_arrays = [pa.array([], type=f.type) for f in full_schema]
            table = pa.table(
                {f.name: arr for f, arr in zip(full_schema, empty_arrays)},
                schema=full_schema,
            )
            pq.write_table(table, str(output_path))
        else:
            # Table layer: plain Parquet via pyarrow
            schema = pa.schema(pa_fields)
            table = pa.table(
                {f.name: pa.array([], type=f.type) for f in schema}, schema=schema
            )
            pq.write_table(table, str(output_path))

        metadata = DatasetMetadata(
            path=str(output_path),
            source_type="vector" if params.geometry_type else "tabular",
            format="parquet",
            crs="EPSG:4326" if params.geometry_type else None,
            feature_count=0,
            geometry_type=geometry_type_name,
        )

        logger.info(
            "Created empty layer: geometry_type=%s, fields=%d",
            geometry_type_name,
            len(params.fields),
        )

        return output_path, metadata

    def _ingest_to_ducklake(
        self: Self,
        user_id: str,
        layer_id: str,
        parquet_path: Path,
    ) -> dict[str, Any]:
        """Override to inject geometry type for empty layers.

        BaseToolRunner._get_table_info detects geometry_type from actual rows
        via ST_GeometryType. Empty layers have 0 rows, so it returns None,
        causing the layer to be classified as "table" instead of "feature".

        We call super() then patch the result with the known geometry type.
        """
        table_info = super()._ingest_to_ducklake(user_id, layer_id, parquet_path)

        # For empty geometry layers, the base class can't detect geometry_type
        # from rows. Inject it from our params so the layer is created as "feature".
        if self._create_params and self._create_params.geometry_type:
            if not table_info.get("geometry_type"):
                geom_name = GEOMETRY_TYPE_MAP[self._create_params.geometry_type]
                table_info["geometry_type"] = geom_name
                if not table_info.get("geometry_column"):
                    table_info["geometry_column"] = "geometry"

        return table_info

    @drops_unrecorded_tables
    def run(self: Self, params: LayerCreateParams) -> dict:
        """Run layer create with custom output name handling.

        Sets result_layer_name from params.name if not already set.
        Stores params on instance so _ingest_to_ducklake can access them.

        Args:
            params: Layer create parameters

        Returns:
            Dict with layer metadata
        """
        if not params.result_layer_name and not params.output_name:
            params.result_layer_name = params.name

        # Store params so _ingest_to_ducklake override can access geometry_type
        self._create_params = params

        result = super().run(params)
        self._write_field_config(params, result)
        return result

    def _write_field_config(
        self: Self, params: LayerCreateParams, result: dict
    ) -> None:
        """Record what the new layer's columns mean.

        Storage type alone does not carry a column's vocabulary or its
        formatting — those live only in `field_config` — so without this a
        layer created with its columns declared up front loses everything the
        create dialog asked for beyond name and kind, while the same column
        added to an existing layer keeps it.

        Written after the layer exists, and never in temp mode, where there is
        no layer row to attach it to. A failure here is logged rather than
        raised: the layer and its columns are real by this point, and the
        vocabulary can be set again from Edit fields.
        """
        if getattr(params, "temp_mode", False):
            return
        layer_id = result.get("layer_id")
        if not layer_id or not params.fields:
            return

        config = {f.name: f.field_config_entry() for f in params.fields}
        try:
            _get_or_create_event_loop().run_until_complete(
                self._persist_field_config(str(layer_id), config)
            )
        except Exception as e:
            logger.warning("Could not write field_config for layer %s: %s", layer_id, e)

    async def _persist_field_config(
        self: Self, layer_id: str, config: dict[str, Any]
    ) -> None:
        """Open a pool, write, and close it again — `run` closed its own."""
        await self._init_db_service()
        try:
            if self.db_service is not None:
                await self.db_service.set_layer_field_config(layer_id, config)
        finally:
            await self._close_db_service()


def main(params: LayerCreateParams) -> dict:
    """Windmill entry point for layer create tool."""
    runner = LayerCreateToolRunner()
    runner.init_from_env()

    try:
        return runner.run(params)
    finally:
        runner.cleanup()
