import warnings

try:
    # Do not make psycopg2 a requirement.
    from psycopg2.extensions import ISQLQuote
except ImportError:
    warnings.warn('psycopg2 not installed', ImportWarning)


from .ewkb import Reader, Typed, Writer
from .geojson import GeoJSON


class Geometry(object, metaclass=Typed):

    @property
    def has_z(self):
        return False

    @property
    def has_m(self):
        return False

    @property
    def has_srid(self):
        return hasattr(self, 'srid')

    @staticmethod
    def from_ewkb(value, cursor=None):
        if not value:
            return None
        return Reader.from_hex(value)

    def to_ewkb(self):
        return Writer.to_hex(self).decode()

    def write_ewkb(self, writer):
        self.write_ewkb_body(writer.clone(self))

    def text(self):
        return "ST_GeometryFromText('{}', {})".format(self.wkt, self.srid)

    # Psycopg2 interface.
    def __conform__(self, protocol):
        if protocol is ISQLQuote:
            return self

    def getquoted(self):
        return "'{}'".format(self.to_ewkb())
    # End Psycopg2 interface.

    def __str__(self):
        return self.wkt

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.wkt)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            other = other.coords
        return self.coords == other

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def wkt(self):
        return "{}({})".format(self.name.upper(), self.wkt_coords)

    @property
    def geojson(self):
        return GeoJSON({
            'type': self.name,
            'coordinates': self.coords
        })
