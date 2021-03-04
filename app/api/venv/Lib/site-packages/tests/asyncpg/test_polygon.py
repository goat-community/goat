import pytest

from postgis import Polygon

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize('expected', [
    (((35, 10), (45, 45), (15, 40), (10, 20), (35, 10)), ((20, 30), (35, 35), (30, 20), (20, 30))),  # noqa
])
async def test_polygon_should_round(connection, expected):
    geom = Polygon(expected, srid=4326)
    await connection.execute('INSERT INTO polygon_async (geom) VALUES ($1)',
                             geom)
    geom = await connection.fetchval('SELECT geom FROM polygon_async WHERE '
                                     'geom=$1', geom, column=0)
    assert geom.coords == expected
