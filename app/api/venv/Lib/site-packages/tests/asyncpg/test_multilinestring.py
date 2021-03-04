import pytest

from postgis import MultiLineString

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize('expected', [
    (((30, 10), (10, 30)), ((40, 10), (10, 40))),
])
async def test_multilinestring_should_round(connection, expected):
    geom = MultiLineString(expected, srid=4326)
    await connection.execute('INSERT INTO multilinestring_async (geom) '
                             'VALUES ($1)', geom)
    geom = await connection.fetchval('SELECT geom FROM multilinestring_async '
                                     'WHERE geom=$1', geom, column=0)
    assert geom.coords == expected
