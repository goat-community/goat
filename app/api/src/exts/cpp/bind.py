import cppimport
from geopandas import GeoDataFrame
from numpy import any, array, double, int32, int64
from pandas.core.frame import DataFrame
from shapely.geometry import Polygon

isochrone_cpp = cppimport.imp("src.exts.cpp.src.isochrone")


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
    # TODO: Find a way to bypass the type conversion (at least for geom). The geometry array conversion is very expensive
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
        only_minimum_cover,
    )
    isochrones = {"geometry": [], "step": []}
    for isochrone in result.isochrone:
        for step, shape in isochrone.shape.items():
            isochrones["geometry"].append(Polygon(shape))
            isochrones["step"].append(step)

    isochrone_gdf = GeoDataFrame(isochrones, crs="EPSG:3857").to_crs("EPSG:4326")
    return isochrone_gdf
