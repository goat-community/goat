from .point import Point
from .multi import Multi


class LineString(Multi):

    TYPE = 2
    SUBCLASS = Point

    @classmethod
    def from_ewkb_body(cls, reader, srid=None):
        return cls([Point.from_ewkb_body(reader)
                   for index in range(reader.read_int())], srid)

    def write_ewkb_body(self, writer):
        writer.write_int(len(self.geoms))
        for geom in self:
            geom.write_ewkb_body(writer)
