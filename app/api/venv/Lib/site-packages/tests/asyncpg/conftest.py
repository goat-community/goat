import asyncpg
import pytest
from postgis import (GeometryCollection, LineString, MultiLineString,
                     MultiPoint, MultiPolygon, Point, Polygon)
from postgis.asyncpg import register

geoms = [Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon,
         GeometryCollection]


@pytest.yield_fixture
async def connection():
    conn = await asyncpg.connect('postgresql://postgres@localhost/test')
    await register(conn)
    tpl = 'CREATE TABLE IF NOT EXISTS {}_async ("geom" geometry({}) NOT NULL)'
    for geom in geoms:
        name = geom.__name__
        await conn.execute(tpl.format(name.lower(), name))
    yield conn
    await conn.close()
