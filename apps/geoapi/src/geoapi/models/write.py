"""Pydantic models for write operations (feature CRUD, column management)."""

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

FieldKind = Literal[
    "string",
    "number",
    "area",
    "perimeter",
    "length",
    "datetime",
    "boolean",
    "formula",
    "serial",
    "uuid",
]

# --- Feature Write Models ---


class FeatureCreate(BaseModel):
    """GeoJSON Feature for creation."""

    type: str = "Feature"
    geometry: Optional[dict[str, Any]] = None
    properties: dict[str, Any] = Field(default_factory=dict)


class FeatureUpdate(BaseModel):
    """Partial properties update for a feature."""

    properties: dict[str, Any]


class FeatureReplace(BaseModel):
    """Full feature replacement (geometry + properties)."""

    type: str = "Feature"
    geometry: Optional[dict[str, Any]] = None
    properties: dict[str, Any] = Field(default_factory=dict)


class BulkFeatureCreate(BaseModel):
    """Batch feature creation."""

    type: str = "FeatureCollection"
    features: list[FeatureCreate]


class BulkDeleteRequest(BaseModel):
    """Batch feature deletion by IDs."""

    ids: list[str]


class FeatureWriteResponse(BaseModel):
    """Response after a feature write operation."""

    id: str
    message: str = "success"


class BulkWriteResponse(BaseModel):
    """Response after a bulk write operation."""

    ids: list[str]
    count: int
    message: str = "success"


class DeleteResponse(BaseModel):
    """Response after a delete operation."""

    id: str
    message: str = "deleted"


class BulkDeleteResponse(BaseModel):
    """Response after a bulk delete operation."""

    count: int
    message: str = "deleted"


# --- Column Management Models ---

# Mapping of user-friendly type names to DuckDB types
COLUMN_TYPE_MAP: dict[str, str] = {
    "string": "VARCHAR",
    "text": "VARCHAR",
    "integer": "INTEGER",
    "int": "INTEGER",
    "bigint": "BIGINT",
    "number": "DOUBLE",
    "float": "DOUBLE",
    "double": "DOUBLE",
    "decimal": "DECIMAL",
    "boolean": "BOOLEAN",
    "bool": "BOOLEAN",
    "date": "DATE",
    "timestamp": "TIMESTAMP WITH TIME ZONE",
    "timestamptz": "TIMESTAMP WITH TIME ZONE",
    "datetime": "TIMESTAMP WITH TIME ZONE",
    "json": "JSON",
}

VALID_COLUMN_TYPES = list(COLUMN_TYPE_MAP.keys())


class ColumnCreate(BaseModel):
    """Create a new column.

    Either `kind` (preferred — public field kind: string/number/area/...)
    or `type` (legacy — raw DuckDB type) must be supplied. When `kind`
    is given, the server resolves the underlying DuckDB type and (for
    computed kinds) the compute SQL via the registry.
    """

    name: str = Field(
        ..., min_length=1, max_length=255, pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$"
    )
    kind: Optional[FieldKind] = None
    type: Optional[str] = Field(
        None,
        description=f"Legacy column type. Valid values: {', '.join(VALID_COLUMN_TYPES)}",
    )
    formula: Optional[str] = Field(
        None,
        max_length=10_000,
        description="SQL expression for kind='formula'. Validated against the "
        "function whitelist and the layer's columns before use.",
    )
    display_config: dict[str, Any] = Field(default_factory=dict)
    allowed_values: Optional[list[Any]] = Field(
        None,
        max_length=500,
        description="Constrain the column to these values. An editor offers "
        "them instead of a free text box, and a write outside the list is "
        "refused unless allow_other is set.",
    )
    allow_other: bool = Field(
        False,
        description="Treat allowed_values as suggestions rather than the only "
        "accepted values.",
    )
    default_value: Optional[Any] = None
    start: Optional[int] = Field(
        None,
        description="First number of a kind='serial' column (default 1). Rows "
        "already in the layer are numbered from it in feature order; new "
        "features continue after the highest number present.",
    )


class ColumnUpdate(BaseModel):
    """Update column properties (rename, display config, formula)."""

    new_name: Optional[str] = Field(
        None, min_length=1, max_length=255, pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$"
    )
    display_config: Optional[dict[str, Any]] = None
    formula: Optional[str] = Field(
        None,
        max_length=10_000,
        description="New SQL expression for a kind='formula' column. The whole "
        "column is recomputed; the column type follows the expression.",
    )
    allowed_values: Optional[list[Any]] = Field(
        None,
        max_length=500,
        description="Replace the column's vocabulary. An empty list removes it, "
        "leaving the column free text again.",
    )
    allow_other: Optional[bool] = None
    default_value: Optional[Any] = Field(
        None,
        description="Value a new feature gets when this column is left blank. "
        "An empty string removes the default. Existing rows are untouched, and "
        "so is the column's DDL default — this is the default of record.",
    )
    kind: Optional[FieldKind] = Field(
        None,
        description="Change the column's kind. Supported: an integer-valued "
        "number column to 'serial' (its values are kept, blank rows are "
        "numbered, new features continue after the highest value), and a "
        "'serial' column back to 'number'. Sent on its own, with `start` at "
        "most.",
    )
    start: Optional[int] = Field(
        None,
        description="With kind='serial': the start of the numbering, used for "
        "blank rows when it is above the column's highest value (default 1).",
    )


class ColumnResponse(BaseModel):
    """Response for column operations."""

    name: str
    type: str
    message: str = "success"
