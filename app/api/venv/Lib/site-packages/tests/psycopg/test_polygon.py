import pytest

from postgis import Polygon


@pytest.mark.parametrize('expected', [
    (((35, 10), (45, 45), (15, 40), (10, 20), (35, 10)), ((20, 30), (35, 35), (30, 20), (20, 30))),  # noqa
])
def test_polyggon_should_round(cursor, expected):
    params = [Polygon(expected, srid=4326)]
    cursor.execute('INSERT INTO polygon (geom) VALUES (%s)', params)
    cursor.execute('SELECT geom FROM polygon WHERE geom=%s', params)
    geom = cursor.fetchone()[0]
    assert geom.coords == expected
