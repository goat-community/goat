import pytest

from postgis import LineString

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize('expected', [
    ((30, 10), (10, 30), (40, 40)),
])
async def test_linestring_should_round(connection, expected):
    geom = LineString(expected, srid=4326)
    await connection.execute('INSERT INTO linestring_async (geom) VALUES ($1)',
                             geom)
    geom = await connection.fetchval('SELECT geom FROM linestring_async WHERE '
                                     'geom=$1', geom, column=0)
    assert geom.coords == expected
