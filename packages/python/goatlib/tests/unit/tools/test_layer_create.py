"""Unit tests for LayerCreate tool.

Tests the layer create functionality including:
- FieldDefinition validation
- LayerCreateParams validation
- LayerCreateToolRunner attributes
- process() method for creating empty layers
"""

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from goatlib.tools.layer_create import (
    FieldDefinition,
    LayerCreateParams,
    LayerCreateToolRunner,
)
from pydantic import ValidationError


class TestFieldDefinition:
    """Test FieldDefinition validation."""

    def test_valid_string_field(self):
        """Valid string field definition."""
        field = FieldDefinition(name="city", type="string")
        assert field.name == "city"
        assert field.type == "string"

    def test_valid_number_field(self):
        """Valid number field definition."""
        field = FieldDefinition(name="population", type="number")
        assert field.name == "population"
        assert field.type == "number"

    def test_invalid_type_rejected(self):
        """Invalid field type should be rejected."""
        with pytest.raises(ValueError):
            FieldDefinition(name="bad", type="boolean")


class TestLayerCreateParams:
    """Test LayerCreateParams validation."""

    BASE_PARAMS = {
        "user_id": "00000000-0000-0000-0000-000000000001",
    }

    def test_valid_point_layer(self):
        """Valid point geometry layer."""
        params = LayerCreateParams(
            **self.BASE_PARAMS,
            name="My Points",
            geometry_type="point",
            fields=[],
        )
        assert params.name == "My Points"
        assert params.geometry_type == "point"

    def test_valid_table_layer(self):
        """Valid table (no geometry) layer."""
        params = LayerCreateParams(
            **self.BASE_PARAMS,
            name="My Table",
            geometry_type=None,
            fields=[],
        )
        assert params.geometry_type is None

    def test_valid_line_layer(self):
        """Valid line geometry layer."""
        params = LayerCreateParams(
            **self.BASE_PARAMS,
            name="My Lines",
            geometry_type="line",
            fields=[],
        )
        assert params.geometry_type == "line"

    def test_valid_polygon_layer(self):
        """Valid polygon geometry layer."""
        params = LayerCreateParams(
            **self.BASE_PARAMS,
            name="My Polygons",
            geometry_type="polygon",
            fields=[],
        )
        assert params.geometry_type == "polygon"

    def test_empty_fields_allowed(self):
        """Empty fields list should be valid."""
        params = LayerCreateParams(
            **self.BASE_PARAMS,
            name="Empty Layer",
            geometry_type="point",
            fields=[],
        )
        assert params.fields == []

    def test_multiple_fields(self):
        """Multiple fields should be accepted."""
        params = LayerCreateParams(
            **self.BASE_PARAMS,
            name="Layer",
            geometry_type="point",
            fields=[
                FieldDefinition(name="name", type="string"),
                FieldDefinition(name="value", type="number"),
            ],
        )
        assert len(params.fields) == 2

    def test_invalid_geometry_rejected(self):
        """Invalid geometry type should be rejected."""
        with pytest.raises(ValueError):
            LayerCreateParams(
                **self.BASE_PARAMS,
                name="Bad",
                geometry_type="multipoint",
                fields=[],
            )

    def test_name_required(self):
        """name is required."""
        with pytest.raises(ValueError):
            LayerCreateParams(
                **self.BASE_PARAMS,
                geometry_type="point",
                fields=[],
            )

    def test_inherits_tool_input_base_fields(self):
        """Should inherit folder_id, project_id, user_id from ToolInputBase."""
        params = LayerCreateParams(
            **self.BASE_PARAMS,
            name="Test",
            geometry_type="point",
            fields=[],
            folder_id="00000000-0000-0000-0000-000000000002",
            project_id="00000000-0000-0000-0000-000000000003",
        )
        assert params.user_id == "00000000-0000-0000-0000-000000000001"
        assert params.folder_id == "00000000-0000-0000-0000-000000000002"
        assert params.project_id == "00000000-0000-0000-0000-000000000003"


class TestLayerCreateToolRunnerAttributes:
    """Test LayerCreateToolRunner class attributes."""

    def test_tool_class_is_none(self):
        """tool_class should be None (no analysis tool)."""
        assert LayerCreateToolRunner.tool_class is None

    def test_output_geometry_type_is_none(self):
        """output_geometry_type should be None (determined at runtime)."""
        assert LayerCreateToolRunner.output_geometry_type is None

    def test_default_output_name(self):
        """default_output_name should be 'New Layer'."""
        assert LayerCreateToolRunner.default_output_name == "New Layer"

    def test_get_feature_layer_type_returns_standard(self):
        """get_feature_layer_type should return 'standard'."""
        runner = LayerCreateToolRunner()
        params = LayerCreateParams(
            user_id="00000000-0000-0000-0000-000000000001",
            name="Test",
            geometry_type="point",
            fields=[],
        )
        assert runner.get_feature_layer_type(params) == "standard"


class TestLayerCreateProcess:
    """Test process() method for creating empty layers."""

    @pytest.fixture
    def runner(self):
        """Create a LayerCreateToolRunner instance."""
        return LayerCreateToolRunner()

    def test_process_point_layer_with_fields(self, runner, tmp_path):
        """Point layer should have geometry column and user-defined fields."""
        params = LayerCreateParams(
            user_id="00000000-0000-0000-0000-000000000001",
            name="Points",
            geometry_type="point",
            fields=[
                FieldDefinition(name="city", type="string"),
                FieldDefinition(name="pop", type="number"),
            ],
        )
        output_path, metadata = runner.process(params, tmp_path)

        assert output_path.exists()
        table = pq.read_table(str(output_path))
        col_names = table.column_names
        assert "geometry" in col_names
        assert "city" in col_names
        assert "pop" in col_names
        assert metadata.feature_count == 0

    def test_process_line_layer(self, runner, tmp_path):
        """Line layer should produce a valid GeoParquet with LineString geometry."""
        params = LayerCreateParams(
            user_id="00000000-0000-0000-0000-000000000001",
            name="Lines",
            geometry_type="line",
            fields=[],
        )
        output_path, metadata = runner.process(params, tmp_path)

        assert output_path.exists()
        table = pq.read_table(str(output_path))
        assert "geometry" in table.column_names
        assert metadata.geometry_type == "LineString"

    def test_process_polygon_layer(self, runner, tmp_path):
        """Polygon layer should produce a valid GeoParquet with Polygon geometry."""
        params = LayerCreateParams(
            user_id="00000000-0000-0000-0000-000000000001",
            name="Polys",
            geometry_type="polygon",
            fields=[],
        )
        output_path, metadata = runner.process(params, tmp_path)

        assert output_path.exists()
        table = pq.read_table(str(output_path))
        assert "geometry" in table.column_names
        assert metadata.geometry_type == "Polygon"

    def test_process_table_layer(self, runner, tmp_path):
        """Table layer should have no geometry column but user fields."""
        params = LayerCreateParams(
            user_id="00000000-0000-0000-0000-000000000001",
            name="Table",
            geometry_type=None,
            fields=[
                FieldDefinition(name="name", type="string"),
                FieldDefinition(name="value", type="number"),
            ],
        )
        output_path, metadata = runner.process(params, tmp_path)

        assert output_path.exists()
        table = pq.read_table(str(output_path))
        assert "geometry" not in table.column_names
        assert "name" in table.column_names
        assert "value" in table.column_names
        assert metadata.feature_count == 0
        assert metadata.geometry_type is None

    def test_process_empty_table_no_fields(self, runner, tmp_path):
        """Table with zero fields should still produce a valid parquet."""
        params = LayerCreateParams(
            user_id="00000000-0000-0000-0000-000000000001",
            name="Empty",
            geometry_type=None,
            fields=[],
        )
        output_path, metadata = runner.process(params, tmp_path)

        assert output_path.exists()
        table = pq.read_table(str(output_path))
        assert len(table) == 0


class TestFieldKinds:
    """The kinds a new layer can carry, and what they are stored as.

    Creation used to accept only string/number, so a `datetime` field became a text
    column and a `boolean` the strings "true"/"false" — a real bug, since adding the
    same column to an existing layer resolves TIMESTAMPTZ and BOOLEAN.
    """

    def test_kind_is_preferred_over_legacy_type(self):
        field = FieldDefinition(name="seen_at", kind="datetime")
        assert field.storage_kind == "datetime"

    def test_legacy_type_still_understood(self):
        # Callers that predate `kind` keep working.
        field = FieldDefinition(name="city", type="string")
        assert field.storage_kind == "string"

    def test_defaults_to_string_when_neither_is_given(self):
        assert FieldDefinition(name="notes").storage_kind == "string"

    def test_computed_and_formula_kinds_are_rejected(self):
        # Their values come from field_config, which nothing writes at create time.
        for kind in ("area", "perimeter", "length", "formula"):
            with pytest.raises(ValidationError):
                FieldDefinition(name="x", kind=kind)

    @pytest.mark.parametrize(
        ("kind", "expected"),
        [
            ("string", pa.string()),
            ("number", pa.float64()),
            ("datetime", pa.timestamp("us", tz="UTC")),
            ("boolean", pa.bool_()),
            ("serial", pa.int64()),
            ("uuid", pa.string()),
        ],
    )
    def test_every_kind_maps_to_its_storage_type(self, kind, expected, tmp_path):
        runner = LayerCreateToolRunner()
        params = LayerCreateParams(
            user_id="00000000-0000-0000-0000-000000000001",
            name="kinds",
            geometry_type=None,
            fields=[FieldDefinition(name="value", kind=kind)],
        )
        output, _ = runner.process(params, tmp_path)
        schema = pq.read_schema(output)
        assert schema.field("value").type == expected


class TestGeneratedKinds:
    """A serial or UUID field declared up front: stored as BIGINT/text, and
    described in field_config the same way geoapi describes one added later, so
    the first feature drawn into the empty layer gets its value."""

    def test_serial_entry_starts_at_one_by_default(self):
        entry = FieldDefinition(name="vorhaben_id", kind="serial").field_config_entry()
        assert entry == {
            "kind": "serial",
            "start": 1,
            "is_computed": False,
            "depends_on": [],
            "display_config": {},
        }

    def test_serial_entry_keeps_its_start(self):
        field = FieldDefinition(name="vorhaben_id", kind="serial", start=1000)
        assert field.field_config_entry()["start"] == 1000

    def test_uuid_entry_has_no_settings(self):
        entry = FieldDefinition(name="uid", kind="uuid").field_config_entry()
        assert entry["kind"] == "uuid"
        assert "start" not in entry

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"kind": "serial", "start": -1},
            {"kind": "serial", "allowed_values": [1, 2]},
            {"kind": "uuid", "start": 5},
            {"kind": "uuid", "allowed_values": ["a"]},
            {"kind": "number", "start": 5},
        ],
    )
    def test_invalid_generated_fields_fail_before_the_layer_exists(self, kwargs):
        with pytest.raises(ValidationError):
            FieldDefinition(name="x", **kwargs)

    def test_the_field_config_written_for_the_new_layer(self, monkeypatch):
        written = {}

        async def persist(layer_id, config):
            written[layer_id] = config

        runner = LayerCreateToolRunner()
        monkeypatch.setattr(runner, "_persist_field_config", persist)
        params = LayerCreateParams(
            user_id="00000000-0000-0000-0000-000000000001",
            name="Vorhaben (Eingabe)",
            geometry_type="point",
            fields=[
                FieldDefinition(name="vorhaben_id", kind="serial", start=100),
                FieldDefinition(name="uid", kind="uuid"),
                FieldDefinition(name="titel", kind="string"),
            ],
        )
        runner._write_field_config(params, {"layer_id": "L1"})
        assert written["L1"]["vorhaben_id"]["kind"] == "serial"
        assert written["L1"]["vorhaben_id"]["start"] == 100
        assert written["L1"]["uid"]["kind"] == "uuid"
        assert written["L1"]["titel"]["kind"] == "string"

    def test_the_empty_layer_numbers_its_first_feature_from_start(self, tmp_path):
        """What geoapi does with the layer next: the first create into the
        created (empty) table gets ``start``, the second ``start + 1``."""
        import duckdb
        from goatlib.utils.generated_fields import GeneratedValues, generated_fields

        params = LayerCreateParams(
            user_id="00000000-0000-0000-0000-000000000001",
            name="Vorhaben",
            geometry_type=None,
            fields=[
                FieldDefinition(name="vorhaben_id", kind="serial", start=100),
                FieldDefinition(name="uid", kind="uuid"),
            ],
        )
        output, _ = LayerCreateToolRunner().process(params, tmp_path)
        config = {f.name: f.field_config_entry() for f in params.fields}

        con = duckdb.connect()
        con.execute(f"CREATE TABLE t AS SELECT * FROM read_parquet('{output}')")
        assert con.execute("DESCRIBE t").fetchall()[0][1] == "BIGINT"
        generator = GeneratedValues(con, "t", generated_fields(config))
        first, second = generator.next_row(), generator.next_row()
        assert (first["vorhaben_id"], second["vorhaben_id"]) == (100, 101)
        assert first["uid"] != second["uid"]
