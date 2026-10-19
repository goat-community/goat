"""Helpers for handling computed columns within feature_write_service.

`parse_computed_columns` turns the layer's `field_config` JSONB blob
into a list of specs (name + dependency-set + compute SQL fragment).
`select_recompute_specs` filters those specs against a set of changed
source columns. `fetch_field_config` reads the JSONB from PG.

This module knows nothing about HTTP. Task D1 wires these helpers into
INSERT/UPDATE statements on customer layer tables.
"""

import json
import logging
from typing import Any
from uuid import UUID

import asyncpg
from goatlib.utils.field_rules import (  # noqa: F401  (re-exported)
    DEPENDS_ON_ANY,
    ComputedColumnSpec,
    allowed_value_columns,
    apply_defaults,
    check_allowed_values,
    column_defaults,
    fill_defaults,
    locked_column_names,
    parse_computed_columns,
    select_recompute_specs,
    validate_allowed_values,
)

logger = logging.getLogger(__name__)


async def fetch_field_config(
    conn: asyncpg.Connection,
    layer_id: UUID,
) -> dict[str, Any]:
    """Read `field_config` JSONB from `customer.layer` for one layer.

    Returns an empty dict if the layer is not found or has no
    field_config. The caller is expected to have already verified the
    layer exists via the normal route auth flow.
    """
    row = await conn.fetchrow(
        "SELECT field_config FROM customer.layer WHERE id = $1::uuid",
        str(layer_id),
    )
    if row is None or row["field_config"] is None:
        return {}
    raw = row["field_config"]
    # asyncpg returns JSONB as either a dict (if a codec is registered) or
    # a JSON string. Handle both.
    if isinstance(raw, str):
        raw = json.loads(raw)
    return dict(raw or {})


def _normalize_layer_uuid(layer_id: str) -> str:
    """Hex-only UUIDs (no dashes) are common in customer.layer; normalise."""
    if "-" not in layer_id and len(layer_id) == 32:
        return f"{layer_id[:8]}-{layer_id[8:12]}-{layer_id[12:16]}-{layer_id[16:20]}-{layer_id[20:]}"
    return layer_id


async def write_field_config(
    conn: asyncpg.Connection,
    layer_id: str,
    field_config: dict[str, Any],
) -> None:
    """Replace the entire `field_config` JSONB for one layer."""
    await conn.execute(
        "UPDATE customer.layer SET field_config = $2::jsonb WHERE id = $1::uuid",
        _normalize_layer_uuid(layer_id),
        json.dumps(field_config),
    )
