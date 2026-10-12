"""SQL preview's alias views belong to the request that made them.

Pooled preview cursors share one DuckDB database. A plain `input_1` view
made by one request could be replaced by another's before the first reads
it, so the views are TEMP: visible to their own cursor only.
"""

import duckdb
import pytest

from processes.services.analytics_service import AnalyticsService


@pytest.mark.parametrize(
    "filter_expr", [None, '{"op": "=", "args": [{"property": "v"}, "mine"]}']
)
def test_an_alias_view_is_invisible_to_other_cursors(filter_expr: str | None) -> None:
    base = duckdb.connect()
    mine, theirs = base.cursor(), base.cursor()
    AnalyticsService()._create_alias_view(
        mine, "input_1", "SELECT 'mine' AS v", filter_expr
    )
    assert mine.execute("SELECT v FROM input_1").fetchall() == [("mine",)]
    with pytest.raises(duckdb.CatalogException):
        theirs.execute("SELECT v FROM input_1")
