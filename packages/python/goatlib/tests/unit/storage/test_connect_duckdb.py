"""Connections from connect_duckdb run axis-order sensitive spatial functions.

DuckDB 2.0 refuses ST_Transform and the spheroid functions until
geometry_always_xy is set. The pools hand out cursors of a base connection, so
the setting must reach them too.
"""

import pytest
from goatlib.storage.ducklake import connect_duckdb

TRANSFORM = "SELECT ST_X(ST_Transform(ST_Point(48.1, 11.5), 'EPSG:4326', 'EPSG:3857'))"


@pytest.mark.unit
def test_a_connection_transforms_with_latitude_first() -> None:
    con = connect_duckdb()

    (x,) = con.execute(TRANSFORM).fetchone()

    # latitude/longitude order: 11.5° E is ~1,280 km east of Greenwich
    assert x == pytest.approx(1_280_174, abs=1)


@pytest.mark.unit
def test_cursors_of_a_connection_transform_too() -> None:
    cursor = connect_duckdb().cursor()

    (x,) = cursor.execute(TRANSFORM).fetchone()

    assert x == pytest.approx(1_280_174, abs=1)
