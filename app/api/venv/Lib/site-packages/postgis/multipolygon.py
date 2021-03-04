from .multi import Multi
from .polygon import Polygon


class MultiPolygon(Multi):

    TYPE = 6
    SUBCLASS = Polygon
