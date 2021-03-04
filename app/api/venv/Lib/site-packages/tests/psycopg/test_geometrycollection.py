from postgis import Point, LineString, Polygon, GeometryCollection

POLYGON = Polygon((
    ((1, 2), (3, 4), (5, 6), (1, 2)),
    ((2, 3), (4, 5), (6, 7), (2, 3))
))

COLLECTION = [
    Point(1, 2),
    LineString(((1, 2), (3, 4))),
    POLYGON
]


def test_geometrycollection_should_round(cursor):
    params = [GeometryCollection(COLLECTION, srid=4326)]
    cursor.execute('INSERT INTO geometrycollection (geom) VALUES (%s)', params)
    cursor.execute('SELECT geom FROM geometrycollection WHERE geom=%s', params)
    geom = cursor.fetchone()[0]
    assert geom == COLLECTION
