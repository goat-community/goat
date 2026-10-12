"""The expression preview's `where_clause` is a condition, not SQL to splice.

It is written into a query on a connection with the whole lake attached, so
anything beyond a condition over the layer's columns is refused before the
layer is even looked up.
"""

import asyncio
from typing import Any

import pytest
from fastapi import HTTPException

from geoapi.routers.expressions import PreviewExpressionRequest, preview_expression


@pytest.mark.parametrize(
    "where_clause",
    [
        "1=1 UNION ALL SELECT pw FROM lake.main.t_secret",
        "1=1; SELECT * FROM lake.main.t_secret",
        "1=1) OR (SELECT count(*) FROM lake.main.t_secret) > 0 --",
        "EXISTS (SELECT 1 FROM lake.main.t_secret)",
        "name IN (SELECT pw FROM read_csv('/etc/passwd'))",
        "current_setting('s3_secret_access_key') = 'x'",
    ],
)
def test_a_filter_that_is_more_than_a_condition_is_refused(where_clause: str) -> None:
    request = PreviewExpressionRequest(expression="1", where_clause=where_clause)
    layer_info: Any = object()  # never reached
    with pytest.raises(HTTPException) as refused:
        asyncio.run(preview_expression(layer_info=layer_info, request=request))
    assert refused.value.status_code == 422
