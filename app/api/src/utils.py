import binascii
import json
import math
import os
import random
import re
import shutil
import string
import subprocess
import tempfile
import time
import uuid
import zipfile
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import IO, Any, Dict, List, Optional

import geopandas
import h3
import numpy as np
import pandas as pd
import pyproj
from fastapi import HTTPException, UploadFile
from geoalchemy2.shape import to_shape
from geojson import Feature, FeatureCollection
from geojson import loads as geojsonloads
from httpx import AsyncClient
from jose import jwt
from numba import njit
from rich import print as print
from shapely import geometry
from shapely.geometry import GeometryCollection, MultiPolygon, Point, Polygon, box
from shapely.ops import transform
from starlette import status
from starlette.responses import Response
from src.core.config import settings
from src.resources.enums import MaxUploadFileSize, MimeTypes
from pydantic import BaseModel
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
import inspect


def optional(*fields):
    def dec(_cls):
        for field in fields:
            _cls.__fields__[field].required = False
            if _cls.__fields__[field].default:
                _cls.__fields__[field].default = None
        return _cls

    if fields and inspect.isclass(fields[0]) and issubclass(fields[0], BaseModel):
        cls = fields[0]
        fields = cls.__fields__
        return dec(cls)
    return dec


async def table_exists(db: AsyncSession, table_name: str) -> bool:
    sql_check_table = (
        select(func.count())
        .where(text("table_name = :table_name"))
        .select_from(text("information_schema.tables"))
    )
    table_exists = await db.execute(sql_check_table, {"table_name": table_name})
    return table_exists.all()[0][0] > 0


def generate_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.API_SECRET_KEY,
        algorithm="HS256",
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(token, settings.API_SECRET_KEY, algorithms=["HS256"])
        return decoded_token["sub"]
    except jwt.JWTError:
        return None


def return_geojson_or_geobuf(
    features: Any,
    return_type: str = "geojson",
) -> Any:
    """
    Return geojson or geobuf
    """

    pass


def to_feature_collection(
    sql_result: Any,
    geometry_name: str = "geom",
    geometry_type: str = "wkb",  # wkb | geojson (wkb is postgis geometry which is stored as hex)
    exclude_properties: List = [],
) -> FeatureCollection:
    """
    Generic method to convert sql result to geojson. Geometry field is expected to be in geojson or postgis hex format.
    """
    if not isinstance(sql_result, list):
        sql_result = [sql_result]

    exclude_properties.append(geometry_name)
    features = []
    for row in sql_result:
        if not isinstance(row, dict):
            dict_row = dict(row)
        else:
            dict_row = row
        geometry = None
        if geometry_type == "wkb":
            geometry = to_shape(dict_row[geometry_name])
        elif geometry_type == "geojson":
            geometry = geojsonloads(dict_row[geometry_name])

        features.append(
            Feature(
                id=dict_row.get("gid") or dict_row.get("id") or 0,
                geometry=geometry,
                properties=without_keys(dict_row, exclude_properties),
            )
        )
    return FeatureCollection(features)


def encode_r5_grid(grid_data: Any) -> bytes:
    """
    Encode raster grid data
    """
    grid_type = "ACCESSGR"
    grid_type_binary = str.encode(grid_type)
    array = np.array(
        [
            grid_data["version"],
            grid_data["zoom"],
            grid_data["west"],
            grid_data["north"],
            grid_data["width"],
            grid_data["height"],
            grid_data["depth"],
        ],
        dtype=np.int32,
    )
    header_bin = array.tobytes()
    # - reshape the data
    grid_size = grid_data["width"] * grid_data["height"]
    if len(grid_data["data"]) == 0:
        data = np.array([], dtype=np.int32)
    else:
        data = grid_data["data"].reshape(grid_data["depth"], grid_size)
        reshaped_data = np.array([])
        for i in range(grid_data["depth"]):
            reshaped_data = np.append(reshaped_data, np.diff(data[i], prepend=0))
        data = reshaped_data.astype(np.int32)
    z_diff_bin = data.tobytes()

    # - encode metadata
    metadata = {
        "accessibility": grid_data.get("accessibility", {}),
        "errors": grid_data.get("errors", []),
        "warnings": grid_data.get("warnings", []),
        "pathSummaries": grid_data.get("pathSummaries", []),
        "scenarioApplicationWarnings": grid_data.get("scenarioApplicationWarnings", []),
        "scenarioApplicationInfo": grid_data.get("scenarioApplicationInfo", []),
    }
    metadata_bin = json.dumps(metadata).encode("utf-8")

    binary_output = b"".join([grid_type_binary, header_bin, z_diff_bin, metadata_bin])
    return binary_output


def decode_r5_grid(grid_data_buffer: bytes) -> dict:
    """
    Decode R5 grid data
    """
    CURRENT_VERSION = 0
    HEADER_ENTRIES = 7
    HEADER_LENGTH = 9  # type + entries
    TIMES_GRID_TYPE = "ACCESSGR"

    # -- PARSE HEADER
    ## - get header type
    header = {}
    header_data = np.frombuffer(grid_data_buffer, count=8, dtype=np.byte)
    header_type = "".join(map(chr, header_data))
    if header_type != TIMES_GRID_TYPE:
        raise ValueError("Invalid grid type")
    ## - get header data
    header_raw = np.frombuffer(grid_data_buffer, count=HEADER_ENTRIES, offset=8, dtype=np.int32)
    version = header_raw[0]
    if version != CURRENT_VERSION:
        raise ValueError("Invalid grid version")
    header["zoom"] = header_raw[1]
    header["west"] = header_raw[2]
    header["north"] = header_raw[3]
    header["width"] = header_raw[4]
    header["height"] = header_raw[5]
    header["depth"] = header_raw[6]
    header["version"] = version

    # -- PARSE DATA --
    gridSize = header["width"] * header["height"]
    # - skip the header
    data = np.frombuffer(
        grid_data_buffer,
        offset=HEADER_LENGTH * 4,
        count=gridSize * header["depth"],
        dtype=np.int32,
    )
    # - reshape the data
    data = data.reshape(header["depth"], gridSize)
    reshaped_data = np.array([], dtype=np.int32)
    for i in range(header["depth"]):
        reshaped_data = np.append(reshaped_data, data[i].cumsum())
    data = reshaped_data
    # - decode metadata
    raw_metadata = np.frombuffer(
        grid_data_buffer,
        offset=(HEADER_LENGTH + header["width"] * header["height"] * header["depth"]) * 4,
        dtype=np.int8,
    )
    metadata = json.loads(raw_metadata.tostring())

    return header | metadata | {"data": data, "errors": [], "warnings": []}


def filter_r5_grid(grid: dict, percentile: int = None, travel_time_limit: int = None) -> dict:
    """
    This function strips the grid to only include one percentile
    and removes empty rows/columns around the bounding box of the largest isochrone.
    It also updates the west/noth/width/height metadata values.
    Padding is added to the grid to avoid edge effects on jsolines.

    :param grid: R5 grid data
    :param percentile: percentile to filter to (Only used if grid has multiple percentiles)
    :param travel_time_limit: travel time limit to filter to

    :return: filtered grid
    """
    if (
        grid["data"] is None
        or grid["width"] is None
        or grid["height"] is None
        or grid["depth"] is None
    ):
        return None

    if grid["depth"] == 1:
        # if only one percentile is requested, return the grid as is
        grid_1d = grid["data"]
    else:
        travel_time_percentiles = [5, 25, 50, 75, 95]
        percentile_index = travel_time_percentiles.index(percentile)
        grid_percentiles = np.reshape(grid["data"], (grid["depth"], -1))
        grid_1d = grid_percentiles[percentile_index]
        grid["depth"] = 1

    # filter grid to only include percentile
    # Convert the data list to a 2D array
    grid_2d = np.array(grid_1d).reshape(grid["height"], grid["width"])

    if travel_time_limit:
        grid_2d = np.where(grid_2d > travel_time_limit, 2147483647, grid_2d)

    # Find the minimum and maximum non-zero row and column indices in the data array
    nonzero_rows, nonzero_cols = np.nonzero(grid_2d != 2147483647)
    min_row, max_row = np.min(nonzero_rows), np.max(nonzero_rows)
    min_col, max_col = np.min(nonzero_cols), np.max(nonzero_cols)
    # Update the west, north, width, and height values
    grid["west"] += min_col - 2
    grid["north"] += min_row - 2
    grid["width"] = max_col - min_col + 5
    grid["height"] = max_row - min_row + 5
    # Create a new 2D array with the dimensions of the figure bounding box
    new_data_arr = np.full((max_row - min_row + 1, max_col - min_col + 1), 2147483647)
    # Copy the non-zero values from the original array to the new array,
    # but only within the figure bounding box
    new_data_arr[nonzero_rows - min_row, nonzero_cols - min_col] = grid_2d[
        nonzero_rows, nonzero_cols
    ]
    # Pad the new data array with 2147483647 to avoid edge effects on jsolines
    new_data_arr = np.pad(new_data_arr, 2, "constant", constant_values=(2147483647,))
    # Convert the new data array back to a list
    new_data_arr = new_data_arr.flatten()
    grid["data"] = new_data_arr
    return grid


def compute_r5_surface(grid: dict, percentile: int) -> np.array:
    """
    Compute single value surface from the grid
    """
    if (
        grid["data"] is None
        or grid["width"] is None
        or grid["height"] is None
        or grid["depth"] is None
    ):
        return None
    travel_time_percentiles = [5, 25, 50, 75, 95]
    percentile_index = travel_time_percentiles.index(percentile)

    if grid["depth"] == 1:
        # if only one percentile is requested, return the grid as is
        surface = grid["data"]
    else:
        grid_percentiles = np.reshape(grid["data"], (grid["depth"], -1))
        surface = grid_percentiles[percentile_index]

    return surface.astype(np.uint8)


@njit(cache=True)
def z_scale(z):
    """
    2^z represents the tile number. Scale that by the number of pixels in each tile.
    """
    PIXELS_PER_TILE = 256
    return 2**z * PIXELS_PER_TILE


@njit(cache=True)
def pixel_to_longitude(pixel_x, zoom):
    """
    Convert pixel x coordinate to longitude
    """
    return (pixel_x / z_scale(zoom)) * 360 - 180


@njit(cache=True)
def pixel_to_latitude(pixel_y, zoom):
    """
    Convert pixel y coordinate to latitude
    """
    lat_rad = math.atan(math.sinh(math.pi * (1 - (2 * pixel_y) / z_scale(zoom))))
    return lat_rad * 180 / math.pi


@njit(cache=True)
def coordinate_from_pixel(input, zoom, round_int=False, web_mercator=False):
    """
    Convert pixel coordinate to longitude and latitude
    """
    if web_mercator:
        x = pixel_x_to_web_mercator_x(input[0], zoom)
        y = pixel_y_to_web_mercator_y(input[1], zoom)
    else:
        x = pixel_to_longitude(input[0], zoom)
        y = pixel_to_latitude(input[1], zoom)
    if round_int:
        x = round(x)
        y = round(y)

    return [x, y]


def buffer(starting_points_gdf, buffer_distance, increment):
    """
    Incrementally buffer a set of points

    Parameters
    ----------
    starting_points_gdf : geopandas.GeoDataFrame. The starting points to buffer
    buffer_distance : float. The initial buffer distance
    increment : float. The increment to add to the buffer distance

    Returns
    -------
    geopandas.GeoDataFrame. The buffered points

    """
    epsg_3857 = pyproj.CRS("EPSG:3857")
    proj_3857 = pyproj.Proj(epsg_3857)
    proj_factors = proj_3857.get_factors(
        starting_points_gdf.iloc[0][0].x, starting_points_gdf.iloc[0][0].y
    )
    # Parallel scale is the ratio of the scale factor at the given latitude to the scale factor at the equator.
    # This is not accurate for very large distances, but should be good enough for our purposes.
    scale_factor = proj_factors.parallel_scale
    starting_points_gdf = starting_points_gdf.to_crs(epsg=3857)
    results = {}
    steps = []
    incremental_shapes = []
    full_shapes = []

    for i in range(increment, buffer_distance + increment, increment):
        steps.append(i // increment)
        # multiply the buffer distance by the scale factor to account for the distortion of the projection.
        # the distance is in meters, on a sphere.
        union_geom = starting_points_gdf.buffer(i * scale_factor).unary_union
        full_shapes.append(union_geom)

    full_gdf = geopandas.GeoDataFrame({"geometry": full_shapes, "steps": steps})
    full_gdf.set_crs(epsg=3857, inplace=True)
    full_gdf = full_gdf.to_crs(epsg=4326)
    results["full"] = full_gdf

    for i in range(len(full_shapes)):
        if i == 0:
            incremental_shapes.append(full_shapes[i])
        else:
            incremental_shapes.append(full_shapes[i].difference(full_shapes[i - 1]))

    incremental_gdf = geopandas.GeoDataFrame({"geometry": incremental_shapes, "steps": steps})
    incremental_gdf.set_crs(epsg=3857, inplace=True)
    incremental_gdf = incremental_gdf.to_crs(epsg=4326)
    results["incremental"] = incremental_gdf

    return results


def coordinate_to_pixel(input, zoom, return_dict=True, round_int=False, web_mercator=False):
    """
    Convert coordinate to pixel coordinate
    """
    if web_mercator:
        x = web_mercator_x_to_pixel_x(input[0], zoom)
        y = web_mercator_y_to_pixel_y(input[1], zoom)
    else:
        x = longitude_to_pixel(input[0], zoom)
        y = latitude_to_pixel(input[1], zoom)
    if round_int:
        x = round(x)
        y = round(y)
    if return_dict:
        return {"x": x, "y": y}
    else:
        return [x, y]


def longitude_to_pixel(longitude, zoom):
    return ((longitude + 180) / 360) * z_scale(zoom)


def latitude_to_pixel(latitude, zoom):
    lat_rad = (latitude * math.pi) / 180
    return ((1 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2) * z_scale(
        zoom
    )


@njit(cache=True)
def web_mercator_x_to_pixel_x(x, zoom):
    return (x + (40075016.68557849 / 2.0)) / (40075016.68557849 / (z_scale(zoom)))


@njit(cache=True)
def web_mercator_y_to_pixel_y(y, zoom):
    return (y - (40075016.68557849 / 2.0)) / (40075016.68557849 / (-1 * z_scale(zoom)))


@njit(cache=True)
def pixel_x_to_web_mercator_x(x, zoom):
    return x * (40075016.68557849 / (z_scale(zoom))) - (40075016.68557849 / 2.0)


@njit(cache=True)
def pixel_y_to_web_mercator_y(y, zoom):
    return y * (40075016.68557849 / (-1 * z_scale(zoom))) + (40075016.68557849 / 2.0)


def geometry_to_pixel(geometry, zoom):
    """
    Convert a geometry to pixel coordinate
    """
    pixel_coordinates = []
    if geometry["type"] == "Point":
        pixel_coordinates.append(
            coordinate_to_pixel(geometry["coordinates"], zoom, return_dict=False, round_int=True)
        )
    if geometry["type"] == "LineString":
        for coordinate in geometry["coordinates"]:
            pixel_coordinates.append(
                np.unique(
                    np.array(
                        coordinate_to_pixel(coordinate, zoom, return_dict=False, round_int=True)
                    ),
                    axis=0,
                )
            )
    elif geometry["type"] == "Polygon":
        for ring in geometry["coordinates"]:
            ring_pixels = np.unique(
                np.array(
                    [
                        coordinate_to_pixel(coord, zoom, return_dict=False, round_int=True)
                        for coord in ring
                    ]
                ),
                axis=0,
            )

            pixel_coordinates.append(ring_pixels)
    else:
        raise ValueError(f"Unsupported geometry type {geometry['type']}")

    return pixel_coordinates


project = pyproj.Transformer.from_crs(
    pyproj.CRS("EPSG:4326"), pyproj.CRS("EPSG:3857"), always_xy=True
).transform

unproject = pyproj.Transformer.from_crs(
    pyproj.CRS("EPSG:3857"), pyproj.CRS("EPSG:4326"), always_xy=True
).transform


def wgs84_to_web_mercator(geometry):
    return transform(project, geometry)


def web_mercator_to_wgs84(geometry):
    return transform(unproject, geometry)


def katana(geometry, threshold, count=0):
    """Split a Polygon into two parts across it's shortest dimension"""
    bounds = geometry.bounds
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    if max(width, height) <= threshold or count == 250:
        # either the polygon is smaller than the threshold, or the maximum
        # number of recursions has been reached
        return [geometry]
    if height >= width:
        # split left to right
        a = box(bounds[0], bounds[1], bounds[2], bounds[1] + height / 2)
        b = box(bounds[0], bounds[1] + height / 2, bounds[2], bounds[3])
    else:
        # split top to bottom
        a = box(bounds[0], bounds[1], bounds[0] + width / 2, bounds[3])
        b = box(bounds[0] + width / 2, bounds[1], bounds[2], bounds[3])
    result = []
    for d in (
        a,
        b,
    ):
        c = geometry.intersection(d)
        if not isinstance(c, GeometryCollection):
            c = [c]
        for e in c:
            if isinstance(e, (Polygon, MultiPolygon)):
                result.extend(katana(e, threshold, count + 1))
    if count > 0:
        return result
    # convert multipart into singlepart
    final_result = []
    for g in result:
        if isinstance(g, MultiPolygon):
            final_result.extend(g)
        else:
            final_result.append(g)
    return final_result


def without_keys(d, keys):
    """
    Omit keys from a dict
    """
    return {x: d[x] for x in d if x not in keys}


def delete_file(file_path: str) -> None:
    """Delete file from disk."""
    try:
        os.remove(file_path)
    except OSError:
        pass


def delete_dir(dir_path: str) -> None:
    """Delete file from disk."""
    try:
        shutil.rmtree(dir_path)
    except OSError:
        pass


def create_dir(dir_path: str) -> None:
    """Create directory if it does not exist."""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def clean_unpacked_zip(dir_path: str, zip_path: str) -> None:
    """Delete unpacked zip file and directory."""
    delete_dir(dir_path)
    delete_file(zip_path)


def print_hashtags():
    print(
        "#################################################################################################################"
    )


def print_info(message: str):
    print(f"[bold green]INFO[/bold green]: {message}")


def print_warning(message: str):
    print(f"[bold red]WARNING[/bold red]: {message}")


def tablify(s):
    # Replace file suffix dot with underscore

    s = s.replace(".", "_")

    # Remove all non-word characters (everything except numbers and letters)
    s = re.sub(r"[^\w\s]", "", s)

    # Replace all runs of whitespace with a single underscore
    s = re.sub(r"\s+", "_", s)

    # Lowercase to prevent having uppercase in table name
    s = s.lower()

    return s


def generate_static_layer_table_name(prefix: str = None):
    if prefix:
        prefix = tablify(prefix)
        # Add sl to prevent havin numbers at the beginning of the table name
        table_name = "sl_" + prefix + "_" + uuid.uuid4().hex
        # The table name limit is 63
        table_name = table_name[:63]
        return table_name
    else:
        return "static_layer_" + uuid.uuid4().hex


def convert_postgist_to_4326(data_frame):
    data_frame.to_crs(epsg=4326, inplace=True)
    data_frame.set_crs(epsg=4326)


def get_file_suffix(file_path):
    # Eg: .zip
    return os.path.splitext(file_path)[-1].lower()


def save_file(data_file: UploadFile):
    """
    Save file to temp directory.
    """
    file_suffix = get_file_suffix(data_file.filename)

    real_file_size = 0
    temp: IO = NamedTemporaryFile(delete=False, suffix=file_suffix)
    for chunk in data_file.file:
        real_file_size += len(chunk)
        if real_file_size > MaxUploadFileSize.max_upload_poi_file_size.value:
            temp.close()
            delete_file(temp.name)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="The uploaded file size is to big the largest allowd size is %s MB."
                % round(MaxUploadFileSize.max_upload_poi_file_size / 1024.0**2, 2),
            )

        temp.write(chunk)
    temp.close()

    return temp.name


def get_zip_directories(zip_file_dir):
    """
    List directories of zip file
    """
    with zipfile.ZipFile(zip_file_dir) as zip_file:
        return [directory for directory in zip_file.namelist() if directory.endswith("/")]


def get_geopandas_uri(file_path):
    file_type = get_file_suffix(file_path)
    if file_type == ".zip":
        file_uri = "zip://" + file_path
        directories = get_zip_directories(file_path)
        if len(directories) == 1:
            # It has only one directory. Let's open it.
            directory = directories[0].replace("/", "")
            file_uri = file_uri + "!" + directory
        elif len(directories) > 1:
            raise HTTPException(
                status_code=400, detail="Several directories inside zip file is not supported."
            )
        else:
            pass
    else:
        file_uri = file_path

    return file_uri


def geopandas_read_file(data_file: UploadFile):
    file_type = get_file_suffix(data_file.filename)
    if file_type != ".zip":
        # Not zip file, don't save it to disk, Open it directly.
        try:
            return geopandas.read_file(data_file.file)
        except Exception as e:
            raise e
    else:
        temp_file_path = save_file(data_file)
        # Generate file path. eg: zip://temp/some_name.zip!some_directory
        file_uri = get_geopandas_uri(temp_file_path)
        try:
            return geopandas.read_file(file_uri)

        except HTTPException as e:
            # It's an HTTP Exception! So raise it to the endpoint.
            raise e

        except Exception as e:
            print(e)
            raise HTTPException(status_code=400, detail="Could not parse file.")

        finally:
            delete_file(temp_file_path)


# https://github.com/uber/h3/issues/275#issuecomment-976886644
def _cover_polygon_h3(polygon: Polygon, resolution: int, intersect_with_centroid: bool):
    """
    Return the set of H3 cells at the specified resolution which completely cover the input polygon.
    """
    result_set = set()
    if intersect_with_centroid is False:
        # Hexes for vertices
        vertex_hexes = [
            h3.geo_to_h3(t[1], t[0], resolution) for t in list(polygon.exterior.coords)
        ]
        # Hexes for edges (inclusive of vertices)
        for i in range(len(vertex_hexes) - 1):
            result_set.update(h3.h3_line(vertex_hexes[i], vertex_hexes[i + 1]))
    # Hexes for internal area
    result_set.update(
        list(h3.polyfill(geometry.mapping(polygon), resolution, geo_json_conformant=True))
    )
    return result_set


def create_h3_grid(
    geometry: geometry,
    h3_resolution: int,
    return_h3_geometries=False,
    return_h3_centroids=False,
    intersect_with_centroid=True,
):
    """Create a list of H3 indexes

    :param geometry: Shapely geometry to create H3 indexes for.
    :param h3_resolution: H3 resolution.
    :param return_h3_geometries: If true, return a GeoDataFrame with the H3 indexes and the corresponding geometries
    :param intersect_with_centroid: If true, will return only the H3 indexes that intersect with the centroid of the geometry

    :return: List of H3 indexes in a GeoDataFrame.
    """

    h3_grid_gdf = geopandas.GeoDataFrame(columns=["h3_index"])

    h3_indexes = []
    if geometry.geom_type == "Polygon":
        h3_index = _cover_polygon_h3(geometry, h3_resolution, intersect_with_centroid)
        h3_indexes.extend(h3_index)
    elif geometry.geom_type == "MultiPolygon":
        for polygon in geometry.geoms:
            h3_index = _cover_polygon_h3(polygon, h3_resolution, intersect_with_centroid)
            h3_indexes.extend(h3_index)
    h3_indexes = list(set(h3_indexes))

    h3_grid_gdf["h3_index"] = h3_indexes

    if return_h3_geometries:
        if return_h3_centroids:
            h3_grid_gdf["geometry"] = h3_grid_gdf["h3_index"].apply(
                lambda x: Point(reversed(h3.h3_to_geo(h=x)))
            )
        else:
            h3_grid_gdf["geometry"] = h3_grid_gdf["h3_index"].apply(
                lambda x: Polygon(h3.h3_to_geo_boundary(h=x, geo_json=True))
            )
        h3_grid_gdf.set_crs(epsg=4326, inplace=True)

    return h3_grid_gdf


def merge_dicts(*dicts):
    """
    Recursively merge any number of dictionaries.
    """
    merged_dict = {}
    for d in dicts:
        for key, value in d.items():
            if (
                key in merged_dict
                and isinstance(merged_dict[key], dict)
                and isinstance(value, dict)
            ):
                merged_dict[key] = merge_dicts(merged_dict[key], value)
            else:
                merged_dict[key] = value
    return merged_dict


def remove_keys(dictionary, keys_to_remove):
    """_summary_
    Remove keys and returns a copy of the dictionary.
    """
    new_dict = dictionary.copy()
    for key in keys_to_remove:
        if key in new_dict:
            new_dict.pop(key)
    return new_dict


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        total_time = te - ts
        if total_time > 1:
            total_time = round(total_time, 2)
            total_time_string = f"{total_time} seconds"
        else:
            time_miliseconds = int((total_time) * 1000)
            total_time_string = f"{time_miliseconds} miliseconds"

        print(f"func: {f.__name__} took: {total_time_string}")

        return result

    return wrap


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


def h3_to_int(h3_array: np.ndarray):
    """
    Convert the h3 array to int array.
    """
    return np.vectorize(lambda x: h3.string_to_h3(str(x)), otypes=["uint64"])(h3_array)


def pad_to_divisible(input_array, kernel_rows, kernel_cols):
    """
    Pad input array to be divisible by kernel size.

    Parameters:
    -----------
    input_array : numpy.ndarray
        Input array to be padded.
    kernel_rows : int
        Kernel size for rows.
    kernel_cols : int
        Kernel size for columns.

    Returns:
    --------
    padded_array : numpy.ndarray
        Padded array that is divisible by the kernel size.
    """

    padding_rows = (kernel_rows - (input_array.shape[0] % kernel_rows)) % kernel_rows
    padding_cols = (kernel_cols - (input_array.shape[1] % kernel_cols)) % kernel_cols

    # calculate even padding on each side of each dimension
    top_padding = padding_rows // 2
    bottom_padding = padding_rows - top_padding
    left_padding = padding_cols // 2
    right_padding = padding_cols - left_padding

    # pad input array
    padded_array = np.pad(
        input_array,
        ((top_padding, bottom_padding), (left_padding, right_padding)),
        mode="constant",
    )

    return padded_array


def downsample_array(arr, new_shape, method="sum"):
    """
    Downsamples a NumPy array to an arbitrary shape and aggregates elements using either the `mean` or `sum` function.

    Parameters:
    -----------
    arr : numpy.ndarray
        Input array to be downsampled.
    new_shape : tuple
        Shape of the output array.
    method : str
        Aggregation method to use. Supported methods are 'mean' and 'sum'.

    Returns:
    --------
    downsampled_arr : numpy.ndarray
        Downsampled array.
    """
    if method not in ["mean", "sum"]:
        raise ValueError(
            f"Unsupported method '{method}' for downsampling array. Supported methods are 'mean' and 'sum'."
        )

    if (
        len(new_shape) != 2
        or not isinstance(new_shape[0], int)
        or not isinstance(new_shape[1], int)
    ):
        raise ValueError("new_shape should be a tuple of two integers.")

    if arr.shape[0] % new_shape[0] != 0 or arr.shape[1] % new_shape[1] != 0:
        raise ValueError("The shape of the input array should be divisible by the new_shape.")

    reshaped_arr = arr.reshape(
        (new_shape[0], arr.shape[0] // new_shape[0], new_shape[1], arr.shape[1] // new_shape[1])
    )

    if method == "mean":
        downsampled_arr = reshaped_arr.mean(axis=(1, 3))
    elif method == "sum":
        downsampled_arr = reshaped_arr.sum(axis=(1, 3))

    return downsampled_arr


def hexlify_file(file_path: str):
    with open(file_path, "rb") as f:
        return binascii.hexlify(f.read()).decode("utf-8")


def zip_converted_files(temp_file_base_path: str, destination_name: str, file_extension: str):
    file_extensions = [file_extension, "txt"]
    if file_extension == "shp":
        file_extensions.extend(["shx", "dbf", "prj"])

    # Create the zip file
    zipfile_path = f"{temp_file_base_path}.zip"

    with zipfile.ZipFile(zipfile_path, "w") as zipf:
        for ext in file_extensions:
            file_path = f"{temp_file_base_path}.{ext}"
            # write_path = os.path.join(destination_name, destination_name + ext)
            if ext == "txt":
                write_path = "info.txt"
            else:
                write_path = f"{destination_name}.{ext}"

            zipf.write(file_path, write_path)

    # Clean up the temp files
    for ext in file_extensions:
        file_path = f"{temp_file_base_path}.{ext}"
        os.remove(file_path)


def generate_info_file(temp_file_base_path: str):
    now = datetime.now()
    info_text = f"""Coordinate Reference System: EPSG:4326
Date: {now.strftime("%B %d, %Y")}
Generated with GOAT (https://github.com/goat-community/goat)
Powered by Plan4Better (https://www.plan4better.com)
"""
    file_path = os.path.join(temp_file_base_path + ".txt")
    with open(file_path, "w") as f:
        f.write(info_text)

    return file_path


def move_first_column_csv_to_last(csv_path: str):
    df = pd.read_csv(csv_path)
    cols = df.columns.tolist()
    cols = cols[1:] + cols[:1]
    df = df[cols]
    df.to_csv(csv_path, index=False)


def convert_csv_to_xlsx(csv_path: str):
    xlsx_path = csv_path.replace(".csv", ".xlsx")
    df = pd.read_csv(csv_path)
    df.to_excel(xlsx_path, index=False)

    # Clean up the temp files
    os.remove(csv_path)


def convert_geojson_to_others_ogr2ogr(
    input_geojson: dict, destination_layer_name: str, output_format: str
):
    temp_file_base_name = tempfile.mktemp()
    options = {
        "geopackage": {"output_suffix": "gpkg", "format_name": "GPKG"},
        "shapefile": {
            "output_suffix": "shp",
            "format_name": "ESRI Shapefile",
            "extra_options": "-lco ENCODING=UTF-8",
        },
        "csv": {
            "output_suffix": "csv",
            "format_name": "CSV",
            "extra_options": "-lco GEOMETRY=AS_WKT",
        },
        "xlsx": {
            "output_suffix": "csv",
            "format_name": "CSV",
            "extra_options": "-lco GEOMETRY=AS_WKT",
        },
        "kml": {
            "output_suffix": "kml",
            "format_name": "KML",
            "extra_options": "-mapFieldType Integer64=Real",
        },
        "geojson": {"output_suffix": "geojson", "format_name": "GeoJSON"},
    }

    output_suffix = options[output_format]["output_suffix"]
    format_name = options[output_format]["format_name"]
    extra_options = options[output_format].get("extra_options", "")

    geojson_temp_file = f"{temp_file_base_name}.geojson"
    output_temp_file = f"{temp_file_base_name}.{output_suffix}"

    with open(geojson_temp_file, "w") as f:
        f.write(json.dumps(input_geojson))

    if output_format != "geojson":
        #
        # Geojson doesn't need to be converted
        #
        command_to_convert = f'ogr2ogr -f "{format_name}" -nln {destination_layer_name} {extra_options} {output_temp_file} {geojson_temp_file}'
        subprocess.check_output(command_to_convert, shell=True)
        delete_file(geojson_temp_file)

        if output_format in ("csv", "xlsx"):
            move_first_column_csv_to_last(output_temp_file)

        if output_format == "xlsx":
            convert_csv_to_xlsx(output_temp_file)
            output_suffix = "xlsx"

    generate_info_file(temp_file_base_name)
    zip_converted_files(temp_file_base_name, destination_layer_name, output_suffix)

    # Read zip file as data and wipe
    zip_file_path = temp_file_base_name + ".zip"
    with open(zip_file_path, "rb") as f:
        data = f.read()
    delete_file(zip_file_path)

    return {
        "data": data,
        "output_suffix": "zip",
    }


def read_results(results, return_type=None):
    """
    results_example = {
        "data": geojson_result,
        "return_type": heatmap_settings.return_type.value,
        "hexlified": False,
        "data_source": "heatmap",
    }
    return geojson or binary content based on return_type
    """
    if not return_type:
        return_type = results["return_type"]

    data = results["data"]

    if return_type == "network":
        return data["network"]

    elif return_type == "grid":
        if results["hexlified"]:
            data = binascii.unhexlify(data["grid"])
        else:
            data = data["grid"]
        return Response(
            data,
            media_type="application/octet-stream",
            headers={"Content-Disposition": "attachment; filename=grid.bin"},
        )

    elif return_type == "geobuf":
        data = geobuf.encode(data["geojson"])
        return Response(
            data,
            media_type=MimeTypes.geobuf.value,
            headers={"Content-Disposition": f"attachment; filename={results['data_source']}.pbf"},
        )

    else:
        converted_data = convert_geojson_to_others_ogr2ogr(
            input_geojson=data["geojson"],
            destination_layer_name=results["data_source"],
            output_format=return_type,
        )
        file_name = f"{results['data_source']}-{return_type}.{converted_data['output_suffix']}"
        # TODO: define the media type based on the output_format
        return Response(
            converted_data["data"],
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={file_name}"},
        )

