"""Aggregation statistics calculation."""

import logging
from typing import Any

import duckdb

from goatlib.analysis.schemas.statistics import (
    AggregationStatsItem,
    AggregationStatsResult,
    SortOrder,
    StatisticsOperation,
)
from goatlib.analysis.statistics.columns import (
    quote_identifier,
    require_column,
    table_column_names,
)

logger = logging.getLogger(__name__)


def calculate_aggregation_stats(
    con: duckdb.DuckDBPyConnection,
    table_name: str,
    operation: StatisticsOperation = StatisticsOperation.count,
    operation_column: str | None = None,
    group_by_column: str | None = None,
    group_by_secondary_column: str | None = None,
    where_clause: str = "TRUE",
    params: list[Any] | None = None,
    order: SortOrder = SortOrder.descendent,
    limit: int = 100,
) -> AggregationStatsResult:
    """Calculate aggregation statistics with optional grouping.

    Args:
        con: DuckDB connection
        table_name: Fully qualified table name (e.g., "lake.my_table")
        operation: Statistical operation (count, sum, mean, min, max, expression)
        operation_column: Column to perform the operation on (required for sum, mean, min, max).
            For expression operation, this contains the raw SQL expression.
        group_by_column: Optional column to group results by
        group_by_secondary_column: Optional secondary column for two-level grouping
        where_clause: SQL WHERE clause condition (default: "TRUE" for all rows)
        params: Optional query parameters for prepared statement
        order: Sort order by operation value (ascendent or descendent)
        limit: Maximum number of grouped values to return

    Returns:
        AggregationStatsResult with items, total_items, and total_count
    """
    # Validate inputs
    if operation not in (StatisticsOperation.count,) and not operation_column:
        raise ValueError(
            f"operation_column is required for operation '{operation.value}'"
        )

    # Written into the SQL, so it must be a number whatever the caller passed:
    # a string here would be SQL.
    limit = max(int(limit), 0)

    # One DESCRIBE for every identifier this call validates. Only the
    # expression operation is exempt: there `operation_column` carries raw SQL
    # that the caller has already put through the expression validator.
    table_columns = table_column_names(con, table_name)

    for identifier_name, identifier_value in (
        ("group_by_column", group_by_column),
        ("group_by_secondary_column", group_by_secondary_column),
    ):
        if identifier_value is None:
            continue
        require_column(
            con, table_name, identifier_value, identifier_name, columns=table_columns
        )

    if operation != StatisticsOperation.expression and operation_column:
        require_column(
            con, table_name, operation_column, "operation_column", columns=table_columns
        )

    # Build the aggregation expression
    if operation == StatisticsOperation.count:
        if operation_column:
            agg_expr = f"COUNT({quote_identifier(operation_column)})"
        else:
            agg_expr = "COUNT(*)"
    elif operation == StatisticsOperation.sum:
        agg_expr = f"SUM({quote_identifier(str(operation_column))})"
    elif operation == StatisticsOperation.mean:
        agg_expr = f"AVG({quote_identifier(str(operation_column))})"
    elif operation == StatisticsOperation.min:
        agg_expr = f"MIN({quote_identifier(str(operation_column))})"
    elif operation == StatisticsOperation.max:
        agg_expr = f"MAX({quote_identifier(str(operation_column))})"
    elif operation == StatisticsOperation.expression:
        # For expression operation, operation_column contains the raw SQL expression
        # Note: The expression should be validated before calling this function
        agg_expr = str(operation_column)
    else:
        raise ValueError(f"Unsupported operation: {operation}")

    # Map order
    order_dir = "DESC" if order == SortOrder.descendent else "ASC"

    # Build the query
    has_secondary = group_by_column and group_by_secondary_column
    if group_by_column:
        group_col = quote_identifier(group_by_column)

        # Query for total count of rows
        count_query = f"""
            SELECT COUNT(*)
            FROM {table_name}
            WHERE {where_clause}
        """

        if has_secondary:
            sec_col = quote_identifier(str(group_by_secondary_column))

            # Total distinct combinations
            total_groups_query = f"""
                SELECT COUNT(*) FROM (
                    SELECT DISTINCT {group_col}, {sec_col}
                    FROM {table_name}
                    WHERE {where_clause}
                ) AS t
            """

            data_query = f"""
                SELECT
                    CAST({group_col} AS VARCHAR) AS grouped_value,
                    CAST({sec_col} AS VARCHAR) AS grouped_secondary_value,
                    {agg_expr} AS operation_value
                FROM {table_name}
                WHERE {where_clause}
                GROUP BY {group_col}, {sec_col}
                ORDER BY operation_value {order_dir}, grouped_value, grouped_secondary_value
                LIMIT {limit}
            """
        else:
            # Query for total number of distinct groups
            total_groups_query = f"""
                SELECT COUNT(DISTINCT {group_col})
                FROM {table_name}
                WHERE {where_clause}
            """

            # Query for aggregation with grouping
            data_query = f"""
                SELECT
                    CAST({group_col} AS VARCHAR) AS grouped_value,
                    {agg_expr} AS operation_value
                FROM {table_name}
                WHERE {where_clause}
                GROUP BY {group_col}
                ORDER BY operation_value {order_dir}, grouped_value
                LIMIT {limit}
            """
    else:
        # Query for total count of rows
        count_query = f"""
            SELECT COUNT(*)
            FROM {table_name}
            WHERE {where_clause}
        """

        # No grouping - just return single aggregation (no params needed)
        total_groups_query = None

        data_query = f"""
            SELECT
                NULL AS grouped_value,
                {agg_expr} AS operation_value
            FROM {table_name}
            WHERE {where_clause}
        """

    logger.debug("Aggregation stats query: %s with params: %s", data_query, params)

    # Execute queries
    if params:
        total_count_result = con.execute(count_query, params).fetchone()
        # total_groups_query may be None (no grouping) or have placeholders
        if total_groups_query:
            total_groups_result = con.execute(total_groups_query, params).fetchone()
        else:
            total_groups_result = (1,)  # Single result when no grouping
        data_result = con.execute(data_query, params).fetchall()
    else:
        total_count_result = con.execute(count_query).fetchone()
        if total_groups_query:
            total_groups_result = con.execute(total_groups_query).fetchone()
        else:
            total_groups_result = (1,)  # Single result when no grouping
        data_result = con.execute(data_query).fetchall()

    total_count = total_count_result[0] if total_count_result else 0
    total_items = total_groups_result[0] if total_groups_result else 0

    # Build result items
    # For expression operations, preserve the raw value (may be string or number).
    # For standard operations, cast to float.
    def _cast_value(val: Any) -> float | str:
        if val is None:
            return 0.0
        if operation == StatisticsOperation.expression:
            try:
                return float(val)
            except (ValueError, TypeError):
                return str(val)
        return float(val)

    if has_secondary:
        items = [
            AggregationStatsItem(
                grouped_value=row[0],
                grouped_secondary_value=row[1],
                operation_value=_cast_value(row[2]),
            )
            for row in data_result
        ]
    else:
        items = [
            AggregationStatsItem(
                grouped_value=row[0],
                grouped_secondary_value=None,
                operation_value=_cast_value(row[1]),
            )
            for row in data_result
        ]

    return AggregationStatsResult(
        items=items,
        total_items=total_items,
        total_count=total_count,
    )
