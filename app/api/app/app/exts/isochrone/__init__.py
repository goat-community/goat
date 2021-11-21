import cppimport
import numpy
from numpy import array, double, dtype, genfromtxt, int64
from pandas.core.frame import DataFrame

isochrone = cppimport.imp("app.exts.isochrone.cpp.isochrone")


def calculate(
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
    isochrone_element_path : dtype :numpy.array{formats: [i8,i8,D,D,D,D], names: [start_id, edge, start_perc, end_perc, start_cost, end_cost, geom]})
        The isochrone path.
    """

    start_vertices = array(start_vertices).astype(int64)
    distance_limits = array(distance_limits).astype(double)
    isochroneclass = isochrone.Isochrone()
    # TODO: Find a way to bypass the type conversion (at least for geom). This step is very expensive
    result = isochroneclass.calculate(
        network["id"],
        network["source"],
        network["target"],
        network["cost"],
        network["reverse_cost"],
        network["geom"],
        start_vertices,
        distance_limits,
        only_minimum_cover,
    )
    return result
