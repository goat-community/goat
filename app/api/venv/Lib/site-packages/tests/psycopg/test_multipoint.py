import pytest

from postgis import MultiPoint


@pytest.mark.parametrize('expected', [
    ((30, 10), (10, 30)),
])
def test_multipoint_should_round(cursor, expected):
    params = [MultiPoint(expected, srid=4326)]
    cursor.execute('INSERT INTO multipoint (geom) VALUES (%s)', params)
    cursor.execute('SELECT geom FROM multipoint WHERE geom=%s', params)
    geom = cursor.fetchone()[0]
    assert geom.coords == expected
