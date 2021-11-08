import cppimport
import numpy
from geopandas.geodataframe import GeoDataFrame
from numpy import array, double, dtype, genfromtxt, int64

isochrone = cppimport.imp("app.exts.isochrone.cpp.isochrone")


def calculate(
    network: GeoDataFrame, start_vertices: array, distance_limits: array, only_minimum_cover=True
) -> array:
    """
    Calculate the isochrone of a network.

    Parameters
    ----------
    network : GeoDataFrame
        The network graph to be used.
    start_vertices : array(int64)
        The starting vertex.
    distance_limits : array(double)
        The distance limits.
    only_minimum_cover : bool (optional, default: True)
        If True, only the minimum cover is returned.

    Returns
    -------
    isochrone_element_path : dtype :numpy.array{formats: [i8,i8,D,D,D,D], names: [start_id, edge, start_perc, end_perc, start_cost, end_cost]})
        The isochrone path.
    """

    # if len(network.shape) < 2:
    #     raise ValueError("Network length must be at least two ")

    # if len(start_vertices.shape) < 1:
    #     raise ValueError("Start vertices length must be at least one ")

    # if len(distance_limits.shape) < 1:
    #     raise ValueError("Distance limits length must be at least one ")

    # i8 = int64, D = double
    dtype_f = ["i8", "i8", "i8", "D", "D"]
    dtype_n = ["id", "source", "target", "cost", "reverse_cost"]
    dt = dtype({"names": dtype_n, "formats": dtype_f})
    start_vertices = array(start_vertices).astype(int64)
    distance_limits = array(distance_limits).astype(double)
    np_network = network.to_records(
        index=False,
        column_dtypes={
            "id": "int64",
            "source": "int64",
            "target": "int64",
            "cost": "complex128",
            "reverse_cost": "complex128",
        },
    ).view(type=numpy.ndarray)
    # c++ wrapper function
    return isochrone.isochrone(np_network, start_vertices, distance_limits, only_minimum_cover)
