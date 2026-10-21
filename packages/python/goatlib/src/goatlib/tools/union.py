"""Union tool for Windmill.

Computes the geometric union of features from input and overlay layers.
Supports self-union when no overlay layer is provided.
"""

import logging
from pathlib import Path
from typing import Any, Optional, Self

from pydantic import ConfigDict, Field

from goatlib.analysis.geoprocessing.union import UnionTool
from goatlib.analysis.schemas.geoprocessing import UnionParams
from goatlib.analysis.schemas.ui import (
    SECTION_INPUT,
    SECTION_OUTPUT,
    SECTION_RESULT,
    UISection,
    ui_field,
    ui_sections,
)
from goatlib.models.io import DatasetMetadata
from goatlib.tools.base import BaseToolRunner
from goatlib.tools.schemas import (
    LayerInputMixin,
    ToolInputBase,
    get_default_layer_name,
)

logger = logging.getLogger(__name__)


class UnionToolParams(ToolInputBase, LayerInputMixin, UnionParams):
    """Parameters for union tool.

    Inherits union options from UnionParams, adds layer context from ToolInputBase.
    input_path/overlay_path/output_path are not used (we use layer IDs instead).
    Overlay layer is optional - if not provided, performs self-union on input.
    """

    model_config = ConfigDict(
        json_schema_extra=ui_sections(
            SECTION_INPUT,
            UISection(id="overlay", order=2, icon="layers"),
            SECTION_RESULT,
            SECTION_OUTPUT,
        )
    )

    input_path: str | None = None  # type: ignore[assignment]
    overlay_path: str | None = None  # type: ignore[assignment]
    output_path: str | None = None

    # Override overlay_layer_id to make it optional for self-union
    overlay_layer_id: Optional[str] = Field(
        None,
        description="Overlay layer UUID. If not provided, performs self-union on input layer.",
        json_schema_extra=ui_field(
            section="overlay",
            field_order=1,
            widget="layer-selector",
        ),
    )
    overlay_layer_filter: dict[str, Any] | None = Field(
        None,
        description="CQL2-JSON filter to apply to the overlay layer",
        json_schema_extra=ui_field(section="overlay", field_order=2, hidden=True),
    )

    # Override to reference overlay_layer_id instead of overlay_path
    overlay_fields_prefix: Optional[str] = Field(
        None,
        description="Prefix to add to overlay field names to avoid naming conflicts.",
        json_schema_extra=ui_field(
            section="overlay",
            field_order=3,
            visible_when={"overlay_layer_id": {"$ne": None}},
        ),
    )

    # Override result_layer_name with tool-specific defaults
    result_layer_name: str | None = Field(
        default=get_default_layer_name("union", "en"),
        description="Name for the union result layer.",
        json_schema_extra=ui_field(
            section="result",
            field_order=1,
            label_key="result_layer_name",
            widget_options={
                "default_en": get_default_layer_name("union", "en"),
                "default_de": get_default_layer_name("union", "de"),
            },
        ),
    )


class UnionToolRunner(BaseToolRunner[UnionToolParams]):
    """Union tool runner for Windmill."""

    tool_class = UnionTool
    output_geometry_type = None  # Depends on input
    output_geometry_follows_input = True
    default_output_name = get_default_layer_name("union", "en")

    @classmethod
    def predict_output_schema(
        cls,
        input_schemas: dict[str, dict[str, str]],
        params: dict[str, Any],
    ) -> dict[str, str]:
        """Predict union output schema.

        Union combines columns from both input and overlay layers.
        If no overlay, performs self-union (just input columns).
        """
        input_layer = input_schemas.get("input_layer_id", {})
        overlay_layer = input_schemas.get("overlay_layer_id", {})

        columns = dict(input_layer)

        # Add overlay columns with prefix if overlay exists
        overlay_prefix = params.get("overlay_fields_prefix", "overlay_")
        for col, dtype in overlay_layer.items():
            if col == "geometry":
                continue  # Skip overlay geometry
            base = f"{overlay_prefix}{col}" if col in columns else col
            out_col = cls.unique_column_name(columns, base)
            columns[out_col] = dtype

        return columns

    def process(
        self: Self, params: UnionToolParams, temp_dir: Path
    ) -> tuple[Path, DatasetMetadata]:
        """Run union analysis."""
        input_path = self.export_layer_to_parquet(
            layer_id=params.input_layer_id,
            user_id=params.user_id,
            cql_filter=params.input_layer_filter,
        )

        # Overlay is optional - if not provided, performs self-union
        overlay_path = None
        if params.overlay_layer_id:
            overlay_path = self.export_layer_to_parquet(
                layer_id=params.overlay_layer_id,
                user_id=params.user_id,
                cql_filter=params.overlay_layer_filter,
            )

        output_path = temp_dir / "output.parquet"

        analysis_params = UnionParams(
            **params.model_dump(
                exclude={
                    "input_path",
                    "overlay_path",
                    "output_path",
                    "user_id",
                    "folder_id",
                    "project_id",
                    "output_name",
                    "input_layer_id",
                    "input_layer_filter",
                    "overlay_layer_id",
                    "overlay_layer_filter",
                }
            ),
            input_path=input_path,
            overlay_path=overlay_path,
            output_path=str(output_path),
        )

        tool = self.tool_class()
        try:
            results = tool.run(analysis_params)
            result_path, metadata = results[0]
            return Path(result_path), metadata
        finally:
            tool.cleanup()


def main(params: UnionToolParams) -> dict:
    """Windmill entry point for union tool."""
    runner = UnionToolRunner()
    runner.init_from_env()

    try:
        return runner.run(params)
    finally:
        runner.cleanup()
