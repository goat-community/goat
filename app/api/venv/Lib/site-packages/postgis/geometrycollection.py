from .geometry import Geometry
from .geojson import GeoJSON


class GeometryCollection(Geometry):

    TYPE = 7

    def __init__(self, geoms, srid=None):
        for geom in geoms:
            if not isinstance(geom, Geometry):
                raise ValueError('{} is not instance of Geometry'.format(geom))
        self.geoms = list(geoms)
        if srid:
            self.srid = srid

    def __iter__(self):
        return self.geoms.__iter__()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            other = other.geoms
        return self.geoms == other

    @property
    def has_z(self):
        return self[0].has_z

    @property
    def has_m(self):
        return self[0].has_m

    def __getitem__(self, item):
        return self.geoms[item]

    @classmethod
    def from_ewkb_body(cls, reader, srid=None):
        return cls([reader.read() for index in range(reader.read_int())], srid)

    def write_ewkb_body(self, writer):
        writer.write_int(len(self.geoms))
        for geom in self:
            geom.write_ewkb(writer)

    @property
    def wkt_coords(self):
        return ', '.join(g.wkt for g in self)

    @property
    def geojson(self):
        return GeoJSON({
            'type': self.name,
            'geometries': [g.geojson for g in self]
        })
