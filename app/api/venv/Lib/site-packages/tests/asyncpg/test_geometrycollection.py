import pytest

from postgis import Point, LineString, Polygon, GeometryCollection

pytestmark = pytest.mark.asyncio


POLYGON = Polygon((
    ((1, 2), (3, 4), (5, 6), (1, 2)),
    ((2, 3), (4, 5), (6, 7), (2, 3))
))

COLLECTION = [
    Point(1, 2),
    LineString(((1, 2), (3, 4))),
    POLYGON
]


async def test_geometrycollection_should_round(connection):
    geom = GeometryCollection(COLLECTION, srid=4326)
    await connection.execute('INSERT INTO geometrycollection_async (geom) '
                             'VALUES ($1)', geom)
    geom = await connection.fetchval('SELECT geom '
                                     'FROM geometrycollection_async '
                                     'WHERE geom=$1', geom, column=0)
    assert geom == COLLECTION
