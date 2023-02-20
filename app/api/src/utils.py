import json
import logging
import math
import os
import random
import re
import shutil
import string
import time
import uuid
import zipfile
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import IO, Any, Dict, List, Optional

import emails
import geobuf
import geopandas
import numba
import numpy as np
import pyproj
from emails.template import JinjaTemplate
from fastapi import HTTPException, UploadFile
from fiona import _err
from geoalchemy2.shape import to_shape
from geojson import Feature, FeatureCollection
from geojson import loads as geojsonloads
from jose import jwt
from numba import njit
from rich import print as print
from sentry_sdk import HttpTransport
from shapely.geometry import GeometryCollection, MultiPolygon, Polygon, box
from shapely.ops import transform
from starlette import status
from starlette.responses import Response

from src.core.config import settings
from src.resources.enums import MaxUploadFileSize, MimeTypes


def send_email_(
    email_to: str,
    subject_template: str = "",
    html_template: str = "",
    environment: Dict[str, Any] = {},
) -> None:
    assert settings.EMAILS_ENABLED, "no provided configuration for email variables"
    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST.upper(), "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    logging.info(f"send email result: {response}")


def send_test_email(email_to: str) -> None:
    project_name = settings.PROJECT_NAME.upper()
    subject = f"{project_name} - Test email"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "test_email.html") as f:
        template_str = f.read()
    send_email_(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={"project_name": settings.PROJECT_NAME.upper(), "email": email_to},
    )


email_content_config = {
    "password_recovery": {
        "url": f"{settings.SERVER_HOST}/reset-password?token=",
        "subject": {
            "en": "Password recovery",
            "de": "Passwort zurücksetzen",
        },
        "template_name": "reset_password",
    },
    "activate_new_account": {
        "url": f"{settings.SERVER_HOST}/activate-account?token=",
        "subject": {
            "en": "Activate your account",
            "de": "Demo aktivieren",
        },
        "template_name": "activate_new_account",
    },
    "account_trial_started": {
        "url": "",
        "subject": {
            "en": "Your GOAT demo is ready to use",
            "de": "Ihre GOAT Demo steht bereit",
        },
        "template_name": "account_trial_started",
    },
    "account_expired": {
        "url": "",
        "subject": {"en": "Account expired", "de": "Demo abgelaufen"},
        "template_name": "account_expired",
    },
    "account_expiring": {
        "url": "",
        "subject": {"en": "Account expiring soon", "de": "Demo bald ablaufen"},
        "template_name": "account_expiring",
    },
}


def send_email(
    type: str,
    email_to: str,
    name: str,
    surname: str,
    token: str = "",
    email_language: str = "en",
) -> None:
    if type not in email_content_config:
        raise ValueError(f"Unknown email type {type}")

    subject = email_content_config[type]["subject"][email_language]
    template_str = ""
    available_email_language = "en"
    template_file_name = email_content_config[type]["template_name"]
    link = email_content_config[type]["url"] + token
    if os.path.isfile(
        Path(settings.EMAIL_TEMPLATES_DIR) / f"{template_file_name}_{email_language}.html"
    ):
        available_email_language = email_language
    try:
        with open(
            Path(settings.EMAIL_TEMPLATES_DIR)
            / f"{template_file_name}_{available_email_language}.html"
        ) as f:
            template_str = f.read()
    except OSError:
        print(f"No template for language {available_email_language}")

    send_email_(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME.upper(),
            "name": name,
            "surname": surname,
            "email": email_to,
            "valid_hours": settings.EMAIL_TOKEN_EXPIRE_HOURS,
            "url": link,
        },
    )


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

    if return_type == "geojson":
        return json.loads(json.dumps(features))
    elif return_type == "geobuf":
        return Response(bytes(geobuf.encode(features)), media_type=MimeTypes.geobuf.value)
    elif return_type == "db_geobuf":
        return Response(bytes(features))
    else:
        raise HTTPException(status_code=400, detail="Invalid return type")


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


def decode_r5_grid(grid_data_buffer: bytes) -> Any:
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
    reshaped_data = np.array([])
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


@njit(cache=True)
def compute_single_value_surface(width, height, depth, data, percentile) -> Any:
    """
    Compute single value surface
    """
    if data is None or width is None or height is None or depth is None:
        return None
    grid_size = width * height
    surface = np.empty(grid_size)
    TRAVEL_TIME_PERCENTILES = [5, 25, 50, 75, 95]
    percentile_index = 0
    if depth == 1:
        percentile = 5  # Walking and cycling
    closest_diff = math.inf
    for index, p in enumerate(TRAVEL_TIME_PERCENTILES):
        current_diff = abs(p - percentile)
        if current_diff < closest_diff:
            percentile_index = index
            closest_diff = current_diff
    for y in np.arange(height):
        for x in np.arange(width):
            index = y * width + x
            if (
                x >= 0
                and x < width
                and y >= 0
                and y < height
                and percentile_index >= 0
                and percentile_index < depth
            ):
                coord = data[(percentile_index * grid_size) + (y * width) + x]
            else:
                coord = math.inf

            surface[index] = coord
    return surface


@njit(cache=True)
def group_opportunities_multi_isochrone(
    west,
    north,
    width,
    surface,
    get_population_sum_pixel,
    get_population_sum_population,
    get_population_sub_study_area_id,
    sub_study_areas_ids,
    MAX_TIME=120,
):
    """
    Return a list of population count for every minute and study-area/polygon
    """

    population_grid_count = np.zeros((len(sub_study_areas_ids), MAX_TIME))
    # - loop population
    for idx, pixel in enumerate(get_population_sum_pixel):
        pixel_x = pixel[1]
        pixel_y = pixel[0]
        x = pixel_x - west
        y = pixel_y - north
        width = width
        index = y * width + x
        time_cost = surface[index]
        if (
            time_cost < 2147483647
            and get_population_sum_population[idx] > 0
            and time_cost <= MAX_TIME
        ):
            for id_sub_study_area_id, sub_study_area_id in enumerate(sub_study_areas_ids):
                if get_population_sub_study_area_id[idx] == sub_study_area_id:
                    population_grid_count[id_sub_study_area_id][
                        int(time_cost) - 1
                    ] += get_population_sum_population[idx]

    for idx, population_per_study_area in enumerate(population_grid_count):
        population_grid_count[idx] = np.cumsum(population_per_study_area)
        population_grid_count[idx][population_grid_count[idx] < 5] = 0

    return population_grid_count


@njit(cache=True)
def group_opportunities_single_isochrone(
    west,
    north,
    width,
    surface,
    get_population_sum_pixel,
    get_population_sum_population,
    get_poi_one_entrance_sum_pixel,
    get_poi_one_entrance_sum_category,
    get_poi_one_entrance_sum_cnt,
    get_poi_more_entrance_sum_pixel,
    get_poi_more_entrance_sum_category,
    get_poi_more_entrance_sum_name,
    get_poi_more_entrance_sum_cnt,
    MAX_TIME=120,
):
    """
    Return a list of amenity count for every minute
    """
    population_grid_count = np.zeros(MAX_TIME)
    # - loop population
    for idx, pixel in enumerate(get_population_sum_pixel):
        pixel_x = pixel[1]
        pixel_y = pixel[0]
        x = pixel_x - west
        y = pixel_y - north
        width = width
        index = y * width + x
        time_cost = surface[index]
        if (
            time_cost < 2147483647
            and get_population_sum_population[idx] > 0
            and time_cost <= MAX_TIME
        ):
            population_grid_count[int(time_cost) - 1] += get_population_sum_population[idx]
    population_grid_count = np.cumsum(population_grid_count)
    population_grid_count[population_grid_count < 5] = 0

    # - loop poi_one_entrance
    poi_one_entrance_list = []
    poi_one_entrance_grid_count = []
    for idx, pixel in enumerate(get_poi_one_entrance_sum_pixel):
        if idx == 0:
            continue
        idx = idx - 1
        pixel_x = pixel[1]
        pixel_y = pixel[0]
        x = pixel_x - west
        y = pixel_y - north
        width = width
        index = y * width + x
        category = get_poi_one_entrance_sum_category[idx]

        if category not in poi_one_entrance_list:
            poi_one_entrance_list.append(category)
            poi_one_entrance_grid_count.append(np.zeros(MAX_TIME))

        time_cost = surface[index]
        if time_cost < 2147483647 and time_cost <= MAX_TIME:
            count = get_poi_one_entrance_sum_cnt[idx]
            poi_one_entrance_grid_count[poi_one_entrance_list.index(category)][
                int(time_cost) - 1
            ] += count

    for index, value in enumerate(poi_one_entrance_grid_count):
        poi_one_entrance_grid_count[index] = np.cumsum(value)

    # - loop poi_more_entrance
    visited_more_entrance_categories = []
    poi_more_entrance_list = []
    poi_more_entrance_grid_count = []
    for idx, pixel in enumerate(get_poi_more_entrance_sum_pixel):
        if idx == 0:
            continue
        idx = idx - 1
        pixel_x = pixel[1]
        pixel_y = pixel[0]
        x = pixel_x - west
        y = pixel_y - north
        width = width
        index = y * width + x
        category = get_poi_more_entrance_sum_category[idx]
        name = get_poi_more_entrance_sum_name[idx]

        if category not in poi_more_entrance_list:
            poi_more_entrance_list.append(category)
            poi_more_entrance_grid_count.append(np.zeros(MAX_TIME))

        time_cost = surface[index]
        category_name = f"{category}_{name}"
        if (
            time_cost < 2147483647
            and category_name not in visited_more_entrance_categories
            and time_cost <= MAX_TIME
        ):
            count = get_poi_more_entrance_sum_cnt[idx]
            poi_more_entrance_grid_count[poi_more_entrance_list.index(category)][
                int(time_cost) - 1
            ] += count
            visited_more_entrance_categories.append(category_name)

    for index, value in enumerate(poi_more_entrance_grid_count):
        poi_more_entrance_grid_count[index] = np.cumsum(value)

    return (
        population_grid_count,
        poi_one_entrance_list,
        poi_one_entrance_grid_count,
        poi_more_entrance_list,
        poi_more_entrance_grid_count,
    )


@njit(cache=True)
def is_inside_sm(polygon, point):
    length = len(polygon) - 1
    dy2 = point[1] - polygon[0][1]
    intersections = 0
    ii = 0
    jj = 1

    while ii < length:
        dy = dy2
        dy2 = point[1] - polygon[jj][1]

        # consider only lines which are not completely above/bellow/right from the point
        if dy * dy2 <= 0.0 and (point[0] >= polygon[ii][0] or point[0] >= polygon[jj][0]):

            # non-horizontal line
            if dy < 0 or dy2 < 0:
                F = dy * (polygon[jj][0] - polygon[ii][0]) / (dy - dy2) + polygon[ii][0]

                if (
                    point[0] > F
                ):  # if line is left from the point - the ray moving towards left, will intersect it
                    intersections += 1
                elif point[0] == F:  # point on line
                    return 2

            # point on upper peak (dy2=dx2=0) or horizontal line (dy=dy2=0 and dx*dx2<=0)
            elif dy2 == 0 and (
                point[0] == polygon[jj][0]
                or (dy == 0 and (point[0] - polygon[ii][0]) * (point[0] - polygon[jj][0]) <= 0)
            ):
                return 2

        ii = jj
        jj += 1

    # print 'intersections =', intersections
    return intersections & 1


@njit(parallel=True)
def is_inside_sm_parallel(points, polygon):
    ln = len(points)
    D = np.empty(ln, dtype=numba.boolean)
    for i in numba.prange(ln):
        D[i] = is_inside_sm(polygon, points[i])
    return D


@njit(cache=True)
def z_scale(z):
    """
    2^z represents the tile number. Scale that by the number of pixels in each tile.
    """
    PIXELS_PER_TILE = 256
    return 2 ** z * PIXELS_PER_TILE


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
    except OSError as e:
        pass


def delete_dir(dir_path: str) -> None:
    """Delete file from disk."""
    try:
        shutil.rmtree(dir_path)
    except OSError as e:
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
                % round(MaxUploadFileSize.max_upload_poi_file_size / 1024.0 ** 2, 2),
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
    return ''.join(random.choice(letters) for i in range(length))
    