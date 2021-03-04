import pytest

from postgis import Point

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize('expected', [
    (1, -2),
    (-1.123456789, 2.987654321),
])
async def test_point_should_round(connection, expected):
    point = Point(*expected, srid=4326)
    await connection.execute('INSERT INTO point_async (geom) VALUES ($1)',
                             point)
    geom = await connection.fetchval('SELECT geom FROM point_async WHERE '
                                     'geom=$1', point, column=0)
    assert geom.coords == expected


async def test_point_with_geography_column(connection):
    await connection.execute('CREATE TABLE geo ("geom" geography(PointZ))')
    point = Point(1, 2, 3, srid=4326)
    await connection.execute('INSERT INTO geo (geom) VALUES ($1)', point)
    geom = await connection.fetchval('SELECT geom FROM geo WHERE geom=$1',
                                     point, column=0)
    assert geom.coords == (1, 2, 3)
    await connection.execute('DROP TABLE geo')
