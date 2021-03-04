import pytest

from postgis import MultiPoint

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize('expected', [
    ((30, 10), (10, 30)),
])
async def test_multipoint_should_round(connection, expected):
    geom = MultiPoint(expected, srid=4326)
    await connection.execute('INSERT INTO multipoint_async (geom) VALUES ($1)',
                             geom)
    geom = await connection.fetchval('SELECT geom FROM multipoint_async WHERE '
                                     'geom=$1', geom, column=0)
    assert geom.coords == expected
