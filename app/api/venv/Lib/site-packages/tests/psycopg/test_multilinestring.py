import pytest

from postgis import MultiLineString


@pytest.mark.parametrize('expected', [
    (((30, 10), (10, 30)), ((40, 10), (10, 40))),
])
def test_multilinestring_should_round(cursor, expected):
    params = [MultiLineString(expected, srid=4326)]
    cursor.execute('INSERT INTO multilinestring (geom) VALUES (%s)', params)
    cursor.execute('SELECT geom FROM multilinestring WHERE geom=%s', params)
    geom = cursor.fetchone()[0]
    assert geom.coords == expected
