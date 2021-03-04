from .geometry import Geometry


class Multi(Geometry):

    __slots__ = ['geoms', 'srid']
    SUBCLASS = None

    def __init__(self, geoms, srid=None):
        self.geoms = [self.SUBCLASS(g, srid=srid) for g in geoms]
        if srid:
            self.srid = srid

    def __iter__(self):
        return iter(self.geoms)

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

    @property
    def wkt_coords(self):
        return ', '.join('({})'.format(g.wkt_coords) for g in self)

    def write_ewkb_body(self, writer):
        writer.write_int(len(self.geoms))
        for geom in self:
            geom.write_ewkb(writer)

    @property
    def coords(self):
        return tuple(g.coords for g in self)
