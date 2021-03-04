import pytest

from postgis import Point


@pytest.mark.parametrize('expected', [
    (1, -2),
    (-1.123456789, 2.987654321),
])
def test_point_should_round(cursor, expected):
    params = [Point(*expected, srid=4326)]
    cursor.execute('INSERT INTO point (geom) VALUES (%s)', params)
    cursor.execute('SELECT geom FROM point WHERE geom=%s', params)
    geom = cursor.fetchone()[0]
    assert geom.coords == expected


@pytest.mark.parametrize('expected', [
    (1, -2, 3),
    (-1.123456789, 2.987654321, 231),
    (1, -2, 0),
])
def test_point_geography_column_should_round(cursor, expected):
    cursor.execute('CREATE TABLE geography_point ("geom" geography(PointZ))')
    params = [Point(*expected, srid=4326)]
    cursor.execute('INSERT INTO geography_point (geom) VALUES (%s)', params)
    cursor.execute('SELECT geom FROM geography_point WHERE geom=%s', params)
    geom = cursor.fetchone()[0]
    assert geom.coords == expected
    cursor.execute('DROP TABLE geography_point')
