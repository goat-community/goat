import cppimport
from numpy import any, array, double, int32, int64
from pandas.core.frame import DataFrame

isochrone_cpp = cppimport.imp("src.exts.cpp.src.isochrone")

import time


def isochrone(
    network: DataFrame, start_vertices: array, distance_limits: array, only_minimum_cover=True
) -> array:
    """
    Calculate the isochrone of a network.

    Parameters
    ----------
    network : Pandas DataFrame
        The network graph to be used.
    start_vertices : array(int64)
        The starting vertex.
    distance_limits : array(double)
        The distance limits.
    only_minimum_cover : bool (optional, default: True)
        If True, only the minimum cover is returned.

    Returns
    -------
    isochrone_gdp : GeoDataFrame
        The isochrone paths.
    """

    start_vertices = array(start_vertices).astype(int64)
    distance_limits = array(distance_limits).astype(double)
    isochroneclass = isochrone_cpp.Isochrone()
    # TODO: Find a way to bypass the type conversion.
    result = isochroneclass.calculate(
        network["id"],
        network["source"],
        network["target"],
        network["cost"],
        network["reverse_cost"],
        network["length"],
        network["geom"],
        start_vertices,
        distance_limits,
        only_minimum_cover
    )

    return result


# 1. (self: src.exts.cpp.src.isochrone.Isochrone, arg0: numpy.ndarray[numpy.int64], arg1: numpy.ndarray[numpy.int64], arg2: numpy.ndarray[numpy.int64], arg3: numpy.ndarray[numpy.float64], arg4: numpy.ndarray[numpy.float64], arg5: numpy.ndarray[numpy.float64], arg6: List[List[List[float[2]]]], arg7: numpy.ndarray[numpy.int64],
# arg8: numpy.ndarray[numpy.float64], arg9: bool) -> src.exts.cpp.src.isochrone.Result
