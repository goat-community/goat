import pytest

from postgis import MultiPolygon

pytestmark = pytest.mark.asyncio

MULTI = (
            (
                ((35, 10), (45, 45), (15, 40), (10, 20), (35, 10)),
                ((20, 30), (35, 35), (30, 20), (20, 30))
            ),
            (
                ((36, 10), (46, 45), (16, 40), (16, 20), (36, 10)),
                ((21, 30), (36, 35), (36, 20), (21, 30))
            ),
        )


@pytest.mark.parametrize('expected', [
    MULTI,
])
async def test_multipolygon_should_round(connection, expected):
    geom = MultiPolygon(expected, srid=4326)
    await connection.execute('INSERT INTO multipolygon_async (geom) '
                             'VALUES ($1)', geom)
    geom = await connection.fetchval('SELECT geom FROM multipolygon_async '
                                     'WHERE geom=$1', geom, column=0)
    assert geom.coords == expected
