"""Class breaks statistics calculation."""

import logging
from typing import Any

import duckdb

from goatlib.analysis.schemas.statistics import ClassBreakMethod, ClassBreaksResult
from goatlib.analysis.statistics.columns import quote_identifier, require_column

logger = logging.getLogger(__name__)


def calculate_class_breaks(
    con: duckdb.DuckDBPyConnection,
    table_name: str,
    attribute: str,
    method: ClassBreakMethod = ClassBreakMethod.quantile,
    num_breaks: int = 5,
    where_clause: str = "TRUE",
    params: list[Any] | None = None,
    strip_zeros: bool = False,
) -> ClassBreaksResult:
    """Calculate classification breaks for a numeric attribute.

    Args:
        con: DuckDB connection
        table_name: Fully qualified table name (e.g., "lake.my_table")
        attribute: Numeric column name to classify
        method: Classification method (quantile, equal_interval, standard_deviation, heads_and_tails)
        num_breaks: Number of classification breaks to calculate
        where_clause: SQL WHERE clause condition (default: "TRUE" for all rows)
        params: Optional query parameters for prepared statement
        strip_zeros: If True, exclude zero values from classification

    Returns:
        ClassBreaksResult with break values and statistics

    Raises:
        ValueError: If `attribute` is not a column of the table.
    """
    attribute = require_column(con, table_name, attribute, "attribute")
    attr_col = quote_identifier(attribute)

    # Build full where clause with null check and optional zero stripping.
    # Infinity and NaN can't be classified and would overflow AVG/STDDEV.
    full_where = f"({where_clause}) AND {attr_col} IS NOT NULL AND isfinite({attr_col})"
    if strip_zeros:
        full_where = f"{full_where} AND {attr_col} != 0"

    # Get basic statistics first
    stats_query = f"""
        SELECT
            MIN({attr_col}) AS min_val,
            MAX({attr_col}) AS max_val,
            AVG({attr_col}) AS mean_val,
            STDDEV({attr_col}) AS std_dev
        FROM {table_name}
        WHERE {full_where}
    """

    logger.debug("Class breaks stats query: %s", stats_query)

    if params:
        stats_result = con.execute(stats_query, params).fetchone()
    else:
        stats_result = con.execute(stats_query).fetchone()

    if not stats_result or stats_result[0] is None:
        return ClassBreaksResult(
            attribute=attribute,
            method=method.value,
            breaks=[],
            min=None,
            max=None,
            mean=None,
            std_dev=None,
        )

    min_val, max_val, mean_val, std_dev = stats_result

    if num_breaks <= 0:
        return ClassBreaksResult(
            attribute=attribute,
            method=method.value,
            breaks=[],
            min=float(min_val) if min_val is not None else None,
            max=float(max_val) if max_val is not None else None,
            mean=float(mean_val) if mean_val is not None else None,
            std_dev=float(std_dev) if std_dev is not None else None,
        )

    # Calculate breaks based on method
    if method == ClassBreakMethod.quantile:
        breaks = _calculate_quantile_breaks(
            con, table_name, attr_col, full_where, params, num_breaks
        )
    elif method == ClassBreakMethod.equal_interval:
        breaks = _calculate_equal_interval_breaks(min_val, max_val, num_breaks)
    elif method == ClassBreakMethod.standard_deviation:
        breaks = _calculate_std_dev_breaks(
            min_val, max_val, mean_val, std_dev, num_breaks
        )
    elif method == ClassBreakMethod.heads_and_tails:
        breaks = _calculate_heads_tails_breaks(
            con, table_name, attr_col, full_where, params, num_breaks, mean_val
        )
    else:
        breaks = []

    return ClassBreaksResult(
        attribute=attribute,
        method=method.value,
        breaks=breaks,
        min=float(min_val) if min_val is not None else None,
        max=float(max_val) if max_val is not None else None,
        mean=float(mean_val) if mean_val is not None else None,
        std_dev=float(std_dev) if std_dev is not None else None,
    )


def _calculate_quantile_breaks(
    con: duckdb.DuckDBPyConnection,
    table_name: str,
    attr_col: str,
    where_clause: str,
    params: list[Any] | None,
    num_breaks: int,
) -> list[float]:
    """Calculate quantile breaks using PERCENTILE_CONT.

    Returns num_breaks internal break points that divide data into
    num_breaks + 1 equal-frequency bins. The min and max values are
    excluded from the breaks (they are returned separately in the result).

    For example, with num_breaks=4 (quintiles = 5 classes):
    percentiles = [0.2, 0.4, 0.6, 0.8]
    """
    # Generate internal percentile values that exclude 0.0 (min) and 1.0 (max)
    # e.g., for 4 breaks (5 classes): 0.2, 0.4, 0.6, 0.8
    percentiles = [i / (num_breaks + 1) for i in range(1, num_breaks + 1)]

    # Build query with multiple PERCENTILE_CONT calls
    percentile_exprs = ", ".join(
        f"PERCENTILE_CONT({p}) WITHIN GROUP (ORDER BY {attr_col})" for p in percentiles
    )
    query = f"""
        SELECT {percentile_exprs}
        FROM {table_name}
        WHERE {where_clause}
    """

    if params:
        result = con.execute(query, params).fetchone()
    else:
        result = con.execute(query).fetchone()

    if result:
        return [float(v) for v in result if v is not None]
    return []


def _calculate_equal_interval_breaks(
    min_val: float, max_val: float, num_breaks: int
) -> list[float]:
    """Calculate equal interval breaks.

    Returns num_breaks internal break points that divide the range into
    num_breaks + 1 equal-width bins. The min and max values are excluded
    from the breaks (they are returned separately in the result).

    For example, with min=0, max=100, num_breaks=4:
    interval = 20, breaks = [20, 40, 60, 80]
    """
    if min_val == max_val:
        return [float(min_val)]

    interval = (max_val - min_val) / (num_breaks + 1)
    breaks = [min_val + interval * i for i in range(1, num_breaks + 1)]
    return [float(b) for b in breaks]


def _calculate_std_dev_breaks(
    min_val: float,
    max_val: float,
    mean_val: float,
    std_dev: float | None,
    num_breaks: int,
) -> list[float]:
    """Calculate standard deviation breaks.

    Returns internal break points at standard deviation intervals around
    the mean. Break points at or beyond min/max are excluded.
    """
    if std_dev is None or std_dev == 0:
        return _calculate_equal_interval_breaks(min_val, max_val, num_breaks)

    # Generate breaks at standard deviation intervals around mean
    breaks = []
    half_breaks = num_breaks // 2

    for i in range(-half_breaks, half_breaks + 1):
        if i == 0:
            continue
        break_val = mean_val + (i * std_dev)
        # Only include internal breaks strictly between min and max
        if min_val < break_val < max_val:
            breaks.append(break_val)

    return sorted([float(b) for b in breaks])


def _calculate_heads_tails_breaks(
    con: duckdb.DuckDBPyConnection,
    table_name: str,
    attr_col: str,
    where_clause: str,
    params: list[Any] | None,
    num_breaks: int,
    initial_mean: float,
) -> list[float]:
    """Calculate heads and tails breaks.

    Heads/tails algorithm iteratively splits data at the mean,
    taking the "head" (above mean) for the next iteration.
    """
    breaks = []
    current_mean = initial_mean

    for _ in range(num_breaks):
        breaks.append(float(current_mean))

        # Get mean of values above current mean
        query = f"""
            SELECT AVG({attr_col})
            FROM {table_name}
            WHERE {where_clause} AND {attr_col} > ?
        """
        query_params = params + [current_mean] if params else [current_mean]

        result = con.execute(query, query_params).fetchone()

        if result and result[0] is not None:
            current_mean = result[0]
        else:
            break

    return sorted(breaks)
