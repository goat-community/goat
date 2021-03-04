import psycopg2

import pytest
from postgis import (GeometryCollection, LineString, MultiLineString,
                     MultiPoint, MultiPolygon, Point, Polygon, register)

db = psycopg2.connect(dbname="test")
cur = db.cursor()
register(db)

geoms = [Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon,
         GeometryCollection]


def pytest_configure(config):
    tpl = 'CREATE TABLE IF NOT EXISTS {} ("geom" geometry({}) NOT NULL)'
    for geom in geoms:
        name = geom.__name__
        cur.execute(tpl.format(name.lower(), name))


def pytest_unconfigure(config):
    for geom in geoms:
        cur.execute('DROP TABLE {}'.format(geom.__name__.lower()))
    db.commit()
    db.close()


@pytest.fixture
def cursor():
    # Make sure tables are clean.
    for geom in geoms:
        cur.execute('TRUNCATE TABLE {}'.format(geom.__name__.lower()))
    return cur
