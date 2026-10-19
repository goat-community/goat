"""What the column endpoints store about a column, and in what order.

The two things that go wrong here are silent: a vocabulary stored as the wrong
type refuses every value the editor then offers, and a refusal raised after the
ALTER TABLE leaves a column no ``field_config`` entry describes.
"""

from contextlib import asynccontextmanager
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest
from fastapi import HTTPException

from geoapi.dependencies import LayerInfo
from geoapi.models import ColumnCreate, ColumnUpdate
from geoapi.services.computed_columns import validate_allowed_values
from geoapi.services.layer_service import LayerMetadata, LayerService

OWNER = UUID("11111111-1111-1111-1111-111111111111")
LAYER_HEX = "abc123def456789012345678901234ab"


@pytest.fixture()
def layer_info() -> LayerInfo:
    return LayerInfo(
        layer_id=LAYER_HEX,
        schema_name=f"user_{OWNER.hex}",
        table_name=f"t_{LAYER_HEX}",
    )


def _metadata() -> LayerMetadata:
    return LayerMetadata(
        layer_id=LAYER_HEX,
        name="Roads",
        geometry_type="LineString",
        bounds=[-180, -90, 180, 90],
        columns=[{"name": "speed", "type": "DOUBLE", "json_type": "number"}],
        user_id=OWNER.hex,
    )


class _FakePool:
    """Enough of an asyncpg pool for the routers' ``async with`` blocks."""

    @asynccontextmanager
    async def acquire(self) -> Any:
        yield MagicMock()


@asynccontextmanager
async def _column_endpoints(
    stored: dict[str, Any] | None = None,
    column_types: dict[str, str] | None = None,
) -> Any:
    """The column endpoints with Postgres, DuckLake and the caches stubbed.

    Yields the recorder: ``written`` is the field_config the endpoint persisted,
    ``ddl`` the DDL it asked for.
    """
    recorder = MagicMock()
    recorder.written = None
    recorder.ddl = MagicMock()
    service = MagicMock()
    service.add_column_with_sql = recorder.ddl
    service.get_column_types = MagicMock(return_value=dict(column_types or {}))

    async def _write(conn: Any, layer_id: str, config: dict[str, Any]) -> None:
        recorder.written = config

    layer_service = MagicMock()
    layer_service._pool = _FakePool()
    layer_service._duckdb_to_json_type = LayerService._duckdb_to_json_type

    with (
        patch(
            "geoapi.routers.features_write.get_write_authorized_metadata",
            AsyncMock(return_value=_metadata()),
        ),
        # An ordinary layer: no bundle owns its columns, so none is protected
        # and none carries a provenance mark.
        patch(
            "geoapi.routers.features_write.layer_is_bundle_member",
            AsyncMock(return_value=False),
        ),
        patch("geoapi.routers.features_write.layer_service", layer_service),
        patch(
            "geoapi.routers.features_write.fetch_field_config",
            AsyncMock(return_value=dict(stored or {})),
        ),
        patch("geoapi.routers.features_write.write_field_config", _write),
        patch("geoapi.routers.features_write.feature_write_service", service),
        patch(
            "geoapi.routers.features_write._invalidate_caches_and_pmtiles",
            AsyncMock(return_value=None),
        ),
        patch(
            "geoapi.routers.features_write._settle_schema_caches",
            AsyncMock(return_value=None),
        ),
    ):
        yield recorder


async def test_a_number_columns_vocabulary_is_stored_as_numbers(layer_info) -> None:
    """The PATCH the editor sends carries only the values, so the column's kind
    has to be resolved from the column itself. Stored as strings, the strict
    ``in`` in ``validate_allowed_values`` refuses every value the dropdown then
    offers."""
    from geoapi.routers.features_write import update_column

    async with _column_endpoints(column_types={"speed": "DOUBLE"}) as recorder:
        await update_column(
            layer_info,
            OWNER,
            ColumnUpdate(allowed_values=[30, 50]),
            columnName="speed",
        )

    entry = recorder.written["speed"]
    assert entry["allowed_values"] == [30, 50]
    assert entry["kind"] == "number"
    # What the editor offers is what a write may set.
    validate_allowed_values(recorder.written, {"speed": 30})


async def test_a_string_columns_vocabulary_is_still_stored_as_strings(
    layer_info,
) -> None:
    from geoapi.routers.features_write import update_column

    async with _column_endpoints(column_types={"surface": "VARCHAR"}) as recorder:
        await update_column(
            layer_info,
            OWNER,
            ColumnUpdate(allowed_values=["asphalt", "gravel"]),
            columnName="surface",
        )

    assert recorder.written["surface"]["allowed_values"] == ["asphalt", "gravel"]
    assert recorder.written["surface"]["kind"] == "string"


async def test_a_refused_vocabulary_leaves_no_orphan_column(layer_info) -> None:
    """The ALTER TABLE is not part of the field_config write, so anything that
    can be refused has to be refused first — otherwise the column exists with
    nothing describing it and the corrected retry fails with "column already
    exists"."""
    from geoapi.routers.features_write import add_column

    async with _column_endpoints() as recorder:
        with pytest.raises(HTTPException) as raised:
            await add_column(
                layer_info,
                OWNER,
                ColumnCreate(name="speed", kind="number", allowed_values=["fast"]),
            )

    assert raised.value.status_code == 400
    assert "not a number" in str(raised.value.detail)
    recorder.ddl.assert_not_called()
    assert recorder.written is None


async def test_an_accepted_vocabulary_is_created_with_the_column(layer_info) -> None:
    from geoapi.routers.features_write import add_column

    async with _column_endpoints() as recorder:
        await add_column(
            layer_info,
            OWNER,
            ColumnCreate(name="speed", kind="number", allowed_values=["30", 50]),
        )

    recorder.ddl.assert_called_once()
    assert recorder.written["speed"]["allowed_values"] == [30, 50]
