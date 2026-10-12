"""Expression builder router for validation and preview.

Provides endpoints for the Formula Builder feature:
- Validate expressions before applying them
- Preview expression results
- Get available functions by category
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, Depends, HTTPException
from goatlib.utils.expressions import (
    FUNCTION_REGISTRY,
    ExpressionEvaluator,
    ExpressionValidator,
    FunctionCategory,
)
from goatlib.utils.sql_validation import validate_sql_expression
from pydantic import BaseModel, Field

from geoapi.dependencies import LayerInfoDep
from geoapi.deps.authz import require_layer_read
from geoapi.ducklake_pool import ducklake_pool
from geoapi.services.layer_service import layer_service

router = APIRouter(prefix="/expressions", tags=["Expressions"])
logger = logging.getLogger(__name__)

# Expression preview runs a blocking DuckLake query; offload it to a thread so
# it never freezes the event loop. Bounded by the shared DuckLake read pool.
_preview_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="expr-preview")


# Request/Response models
class ValidateExpressionRequest(BaseModel):
    """Request to validate an expression."""

    expression: str = Field(..., description="The SQL expression to validate")
    column_names: list[str] = Field(
        ..., description="List of valid column names in the table"
    )
    column_types: dict[str, str] | None = Field(
        None,
        description="Dict mapping column names to their JSON types "
        "(e.g., {'population': 'integer', 'name': 'string'})",
    )
    geometry_column: str | None = Field(
        "geometry", description="Name of the geometry column"
    )


class ValidateExpressionResponse(BaseModel):
    """Response from expression validation."""

    valid: bool = Field(..., description="Whether the expression is valid")
    expression: str = Field(..., description="The validated expression")
    errors: list[dict] = Field(
        default_factory=list, description="List of validation errors"
    )
    warnings: list[str] = Field(
        default_factory=list, description="List of validation warnings"
    )
    referenced_columns: list[str] = Field(
        default_factory=list, description="Columns referenced in the expression"
    )
    used_functions: list[str] = Field(
        default_factory=list, description="Functions used in the expression"
    )


class PreviewExpressionRequest(BaseModel):
    """Request to preview an expression result."""

    expression: str = Field(..., description="The SQL expression to preview")
    where_clause: str | None = Field(
        None, description="Optional WHERE clause to filter rows"
    )
    limit: int = Field(10, ge=1, le=100, description="Number of rows to preview")


class PreviewRow(BaseModel):
    """A single row in the preview result."""

    row_number: int = Field(..., description="Row number")
    result: str | int | float | bool | None = Field(
        ..., description="Expression result"
    )
    context: dict = Field(default_factory=dict, description="Referenced column values")


class PreviewExpressionResponse(BaseModel):
    """Response from expression preview."""

    success: bool = Field(..., description="Whether the preview succeeded")
    expression: str = Field(..., description="The previewed expression")
    result_type: str | None = Field(None, description="DuckDB type of the result")
    rows: list[PreviewRow] = Field(default_factory=list, description="Preview rows")
    column_names: list[str] = Field(
        default_factory=list, description="Column names in context"
    )
    error: str | None = Field(None, description="Error message if preview failed")


class FunctionDocResponse(BaseModel):
    """Function documentation response."""

    name: str = Field(..., description="Function name")
    category: str = Field(..., description="Function category")
    syntax: str = Field(..., description="Function syntax")
    example: str = Field(..., description="Usage example")
    description_key: str = Field(..., description="i18n key for description")
    parameters: list[dict] = Field(
        default_factory=list, description="Parameter documentation"
    )


class FunctionListResponse(BaseModel):
    """Response with list of available functions."""

    functions: dict[str, list[FunctionDocResponse]] = Field(
        ..., description="Functions grouped by category"
    )
    total: int = Field(..., description="Total number of functions")


class ValidateExpressionSimpleRequest(BaseModel):
    """Simple request to validate an expression (for use with collection endpoint)."""

    expression: str = Field(..., description="The SQL expression to validate")


@router.post(
    "/validate",
    summary="Validate an expression",
    response_model=ValidateExpressionResponse,
)
async def validate_expression(
    request: ValidateExpressionRequest,
) -> ValidateExpressionResponse:
    """Validate a SQL expression against the function whitelist and column names.

    This endpoint checks:
    - Syntax correctness
    - Security (no DDL, DML, file access, etc.)
    - Function whitelist compliance
    - Column reference validity
    - Function parameter type compatibility (if column_types provided)

    Returns validation result with any errors and suggestions.
    """
    validator = ExpressionValidator(
        column_names=request.column_names,
        geometry_column=request.geometry_column,
        column_types=request.column_types,
    )
    result = validator.validate(request.expression)

    return ValidateExpressionResponse(
        valid=result.valid,
        expression=result.expression,
        errors=[
            {
                "message": e.message,
                "code": e.code,
                "position": e.position,
                "suggestion": e.suggestion,
            }
            for e in result.errors
        ],
        warnings=result.warnings,
        referenced_columns=list(result.referenced_columns),
        used_functions=list(result.used_functions),
    )


@router.post(
    "/validate/{collectionId}",
    summary="Validate an expression for a collection",
    response_model=ValidateExpressionResponse,
    dependencies=[Depends(require_layer_read)],
)
async def validate_expression_for_collection(
    layer_info: LayerInfoDep,
    request: ValidateExpressionSimpleRequest,
) -> ValidateExpressionResponse:
    """Validate a SQL expression for a specific collection.

    Automatically uses the collection's column names and types for validation,
    including function parameter type checking.
    """
    # Get layer metadata
    metadata = await layer_service.get_layer_metadata(layer_info)
    if not metadata:
        raise HTTPException(status_code=404, detail="Collection not found")

    validator = ExpressionValidator(
        column_names=metadata.column_names,
        geometry_column=metadata.geometry_column,
        column_types=metadata.column_types,
    )
    result = validator.validate(request.expression)

    return ValidateExpressionResponse(
        valid=result.valid,
        expression=result.expression,
        errors=[
            {
                "message": e.message,
                "code": e.code,
                "position": e.position,
                "suggestion": e.suggestion,
            }
            for e in result.errors
        ],
        warnings=result.warnings,
        referenced_columns=list(result.referenced_columns),
        used_functions=list(result.used_functions),
    )


@router.post(
    "/preview/{collectionId}",
    summary="Preview expression result",
    response_model=PreviewExpressionResponse,
    dependencies=[Depends(require_layer_read)],
)
async def preview_expression(
    layer_info: LayerInfoDep,
    request: PreviewExpressionRequest,
) -> PreviewExpressionResponse:
    """Preview an expression result on actual data.

    Runs the expression on a sample of rows and returns:
    - The computed result for each row
    - Referenced column values for context
    - The inferred result type

    The expression is validated before execution.
    """
    # The filter is written into the query on a connection with the whole
    # lake attached: a condition over this layer's columns, nothing more.
    if request.where_clause:
        try:
            validate_sql_expression(request.where_clause)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e

    try:
        # Get layer metadata for validation
        metadata = await layer_service.get_layer_metadata(layer_info)
        if not metadata:
            raise HTTPException(status_code=404, detail="Collection not found")

        # Run the blocking DuckLake preview in a thread pool so it doesn't
        # freeze the event loop (and stall tiles/features on the same worker).
        def _run_preview():
            with ducklake_pool.connection() as con:
                evaluator = ExpressionEvaluator(
                    con=con,
                    table_name=layer_info.full_table_name,
                    column_names=metadata.column_names,
                    geometry_column=metadata.geometry_column,
                )
                return evaluator.preview(
                    expression=request.expression,
                    where_clause=request.where_clause,
                    limit=request.limit,
                )

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(_preview_executor, _run_preview)

        return PreviewExpressionResponse(
            success=result.success,
            expression=result.expression,
            result_type=result.result_type,
            rows=[
                PreviewRow(
                    row_number=row.row_number,
                    result=row.result,
                    context=row.context,
                )
                for row in result.rows
            ],
            column_names=result.column_names,
            error=result.error,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error previewing expression")
        return PreviewExpressionResponse(
            success=False,
            expression=request.expression,
            error=str(e),
        )


@router.get(
    "/functions",
    summary="Get available functions",
    response_model=FunctionListResponse,
)
async def get_functions() -> FunctionListResponse:
    """Get all available functions grouped by category.

    Returns the complete function registry with documentation
    for each function, including syntax, examples, and parameters.
    """
    functions_by_category: dict[str, list[FunctionDocResponse]] = {}

    for func_name, func_doc in FUNCTION_REGISTRY.items():
        category = func_doc.category.value

        if category not in functions_by_category:
            functions_by_category[category] = []

        functions_by_category[category].append(
            FunctionDocResponse(
                name=func_doc.name,
                category=category,
                syntax=func_doc.syntax,
                example=func_doc.example,
                description_key=func_doc.description_key,
                parameters=[
                    {
                        "name": p.name,
                        "type": p.type,
                        "description_key": p.description_key,
                        "optional": p.optional,
                    }
                    for p in func_doc.parameters
                ],
            )
        )

    # Sort functions within each category
    for category in functions_by_category:
        functions_by_category[category].sort(key=lambda f: f.name)

    return FunctionListResponse(
        functions=functions_by_category,
        total=len(FUNCTION_REGISTRY),
    )


@router.get(
    "/functions/{category}",
    summary="Get functions by category",
    response_model=list[FunctionDocResponse],
)
async def get_functions_by_category(
    category: FunctionCategory,
) -> list[FunctionDocResponse]:
    """Get functions for a specific category.

    Available categories:
    - math: Mathematical functions (ABS, ROUND, FLOOR, etc.)
    - string: String manipulation (UPPER, LOWER, TRIM, etc.)
    - date: Date/time functions (NOW, DATE_PART, etc.)
    - aggregate: Aggregation functions (SUM, AVG, COUNT, etc.)
    - window: Window functions (ROW_NUMBER, RANK, etc.)
    - spatial: Spatial functions (ST_Area, ST_Length, etc.)
    - conditional: Conditional logic (CASE, COALESCE, NULLIF, etc.)
    """
    result = []
    for func_name, func_doc in FUNCTION_REGISTRY.items():
        if func_doc.category == category:
            result.append(
                FunctionDocResponse(
                    name=func_doc.name,
                    category=func_doc.category.value,
                    syntax=func_doc.syntax,
                    example=func_doc.example,
                    description_key=func_doc.description_key,
                    parameters=[
                        {
                            "name": p.name,
                            "type": p.type,
                            "description_key": p.description_key,
                            "optional": p.optional,
                        }
                        for p in func_doc.parameters
                    ],
                )
            )

    result.sort(key=lambda f: f.name)
    return result
