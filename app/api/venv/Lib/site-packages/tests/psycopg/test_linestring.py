import pytest

from postgis import LineString


@pytest.mark.parametrize('expected', [
    ((30, 10), (10, 30), (40, 40)),
])
def test_linestring_should_round(cursor, expected):
    params = [LineString(expected, srid=4326)]
    cursor.execute('INSERT INTO linestring (geom) VALUES (%s)', params)
    cursor.execute('SELECT geom FROM linestring WHERE geom=%s', params)
    geom = cursor.fetchone()[0]
    assert geom.coords == expected
