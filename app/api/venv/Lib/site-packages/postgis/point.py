from .geometry import Geometry


class Point(Geometry):

    __slots__ = ['x', 'y', 'z', 'm', 'srid']
    TYPE = 1

    def __init__(self, x, y=None, z=None, m=None, srid=None):
        if y is None and isinstance(x, (tuple, list)):
            x, y, *extra = x
            if extra:
                z, *extra = extra
                if extra:
                    m = extra[0]
        self.x = float(x)
        self.y = float(y)
        self.z = int(z) if z is not None else None
        self.m = int(m) if m is not None else None
        if srid is not None:
            self.srid = srid

    def __getitem__(self, item):
        if item in (0, 'x'):
            return self.x
        elif item in (1, 'y'):
            return self.y
        elif item in (2, 'z'):
            return self.z
        elif item in (3, 'm'):
            return self.m

    def __iter__(self):
        return iter(self.values())

    _keys = ['x', 'y', 'z', 'm']

    def keys(self):
        return [k for k in self._keys if self[k] is not None]

    def values(self):
        return tuple(self[k] for k in self.keys())

    @property
    def has_z(self):
        return self.z is not None

    @classmethod
    def from_ewkb_body(cls, reader, srid=None):
        return cls(reader.read_double(), reader.read_double(),
                   reader.read_double() if reader.has_z else None,
                   reader.read_double() if reader.has_m else None,
                   srid)

    def write_ewkb_body(self, writer):
        writer.write_double(self.x)
        writer.write_double(self.y)
        if self.z is not None:
            writer.write_double(self.z)
        if self.m is not None:
            writer.write_double(self.m)

    @property
    def wkt_coords(self):
        return ' '.join(map(str, self.coords))

    @property
    def coords(self):
        return self.values()
