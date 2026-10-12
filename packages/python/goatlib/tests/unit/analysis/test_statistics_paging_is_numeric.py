"""`limit` and `offset` reach statistics SQL as numbers, never as text.

Both are written into the query on a connection that can see other tables,
so a string carrying SQL must fail instead of running.
"""

import duckdb
import pytest
from goatlib.analysis.schemas.statistics import StatisticsOperation
from goatlib.analysis.statistics.aggregation_stats import calculate_aggregation_stats
from goatlib.analysis.statistics.unique_values import calculate_unique_values

PAYLOADS = [
    "0; SELECT pw, 1 FROM victim.secret --",
    "(SELECT count(*) FROM victim.secret)",
]


@pytest.fixture
def con() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute("CREATE TABLE t AS SELECT 'a' AS name")
    con.execute("CREATE SCHEMA victim")
    con.execute("CREATE TABLE victim.secret AS SELECT 'hunter2' AS pw")
    return con


@pytest.mark.parametrize("payload", PAYLOADS)
def test_unique_values_paging_must_be_numeric(
    con: duckdb.DuckDBPyConnection, payload: str
) -> None:
    with pytest.raises(ValueError):
        calculate_unique_values(con, "t", "name", offset=payload)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        calculate_unique_values(con, "t", "name", limit=payload)  # type: ignore[arg-type]
    result = calculate_unique_values(con, "t", "name", limit=10, offset=0)
    assert [v.value for v in result.values] == ["a"]


@pytest.mark.parametrize("payload", PAYLOADS)
def test_aggregation_limit_must_be_numeric(
    con: duckdb.DuckDBPyConnection, payload: str
) -> None:
    with pytest.raises(ValueError):
        calculate_aggregation_stats(
            con,
            "t",
            operation=StatisticsOperation.count,
            group_by_column="name",
            limit=payload,  # type: ignore[arg-type]
        )
