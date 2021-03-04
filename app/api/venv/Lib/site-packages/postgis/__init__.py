"Postgis helpers for psycopg2 and asyncpg."
from .geometry import Geometry
from .geometrycollection import GeometryCollection
from .linestring import LineString
from .multilinestring import MultiLineString
from .multipoint import MultiPoint
from .multipolygon import MultiPolygon
from .point import Point
from .polygon import Polygon
try:
    from .psycopg import register  # Retrocompat.
except ImportError:
    pass

__all__ = ['Geometry', 'register', 'Point', 'LineString', 'Polygon',
           'MultiPoint', 'MultiLineString', 'MultiPolygon',
           'GeometryCollection']

try:
    import pkg_resources
except ImportError:  # pragma: no cover
    pass
else:
    if __package__:
        VERSION = pkg_resources.get_distribution(__package__).version
