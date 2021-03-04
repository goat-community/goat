from .multi import Multi
from .linestring import LineString


class MultiLineString(Multi):

    TYPE = 5
    SUBCLASS = LineString
