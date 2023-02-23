import asyncio
import base64
import math
import random
import time
from enum import Enum
from pathlib import Path

import aiofiles
import geopandas as gpd
import h3
import numpy as np
from aiohttp import BasicAuth, ClientError, ClientSession
from pydantic import BaseModel, Field
from shapely.geometry import box

from src.core.config import settings
from src.db.session import legacy_engine
from src.utils import create_h3_grid, decode_r5_grid, print_info, web_mercator_to_wgs84

# -- R5 CONFIGURATION --
RESOLUTION = 9
MAX_DISTANCE_FROM_CENTER = 80000  # in meters (used to calculate the bounds from each hex center)
WALKING_SPEED = 1.39  # in m/s
MAX_WALK_TIME = 20  # in minutes
PAYLOAD = {
    "accessModes": "WALK",
    "transitModes": "BUS,TRAM,SUBWAY,RAIL",
    "bikeSpeed": 4.166666666666667,
    "walkSpeed": WALKING_SPEED,
    "bikeTrafficStress": 4,
    "date": "2022-05-16",
    "fromTime": 25200,
    "toTime": 39600,
    "maxTripDurationMinutes": 120,
    "decayFunction": {
        "type": "logistic",
        "standard_deviation_minutes": 12,
        "width_minutes": 10,
    },
    "destinationPointSetIds": [],
    # BOUNDS ARE DYNAMICALLY SET FROM EACH HEX CENTER
    "bounds": {
        "north": 48.27059464660387,
        "south": 48.03915718648435,
        "east": 11.327192290815145,
        "west": 11.756388821971976,
    },
    "directModes": "WALK",
    "egressModes": "WALK",
    "fromLat": 48.1502132,  # DYNAMICALLY SET
    "fromLon": 11.5696284,  # DYNAMICALLY SET
    "zoom": 9,
    "maxBikeTime": 20,
    "maxRides": 4,
    "maxWalkTime": MAX_WALK_TIME,
    "monteCarloDraws": 200,
    "percentiles": [5, 25, 50, 75, 95],
    "variantIndex": -1,
    "workerVersion": "v6.4",
    "projectId": "630c0014aad8682ef8461b44",
}


class IsochroneStartingPointCoord(BaseModel):
    lat: float = Field(..., gt=-90, lt=90)
    lon: float = Field(..., gt=-180, lt=180)


class PrepareBulkObjType(str, Enum):
    TRANSIT = "transit"
    WALKING = "walking"


user, password = (
    base64.b64decode(settings.R5_AUTHORIZATION.split(" ")[1]).decode("utf-8").split(":")
)


def filter_r5_grid(grid: dict, percentile: int, travel_time_limit: int = None):
    """
    This function strips the grid to only include one percentile and removes empty rows/columns around the bounding box of the largest isochrone.
    It also updates the west/noth/width/height metadata values.
    Padding is added to the grid to avoid edge effects on jsolines.
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
        grid_1d = grid["data"]
    else:
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


async def prepare_bulk_objs(
    bulk_resolution: int,
    calculation_resolution: int,
    study_area_ids: list[int] = None,
    bulk_obj_type: PrepareBulkObjType = PrepareBulkObjType.WALKING,
    starting_point_buffer: float = 1668,
) -> dict:

    """Creates the starting points for the traveltime matrix calculation.

    Args:
        bulk_resolution (int): H3 resolution for the bulk grids.
        calculation_resolution (int): H3 resolution for the calculation grids.
        study_area_ids (list[int], optional): List of study area ids. Defaults to None and will use all study area.
        bulk_obj_type (PrepareBulkObjType, optional): Type of bulk object. Defaults to PrepareBulkObjType.WALKING.
        starting_point_buffer (float): Buffer size in meters around the starting point. Defaults to 1668 meters (20 minutes walking at 1.39 m/s)

    Raises:
        ValueError: If the bulk resolution is smaller than the calculation resolution.

    Returns:
        dict: Hierarchical structure of starting points for the calculation using the bulk resolution as parent and calculation resolution as children.
    """
    if bulk_resolution >= calculation_resolution:
        raise ValueError(
            "Resolution of parent grid cannot be smaller then resolution of children grid."
        )

    # - FETCH STUDY AREA GEOMETRY

    # Buffer size for the study area. This is computed in order to include all hex res 6 hexagon within the study area.
    # Multiplying the edge length of a hexagon with 2 will give the diameter of the hexagon.
    study_area_buffer = h3.edge_length(bulk_resolution, "m") * 2

    if bulk_obj_type == PrepareBulkObjType.TRANSIT:
        # fetch study area for transit bulk objects
        sql_query = f"""
        DROP TABLE IF EXISTS tmp_study_area_buffer;
        CREATE TEMP TABLE tmp_study_area_buffer AS  
        SELECT st_transform(st_buffer(st_transform(sa.geom, 3857),{starting_point_buffer}),4326) AS geom, sa.id as id
        FROM basic.study_area sa; 
        CREATE INDEX ON tmp_study_area_buffer USING GIST(geom); 	
        SELECT st_union(st_transform(st_buffer(st_transform(st.stop_loc, 3857),{study_area_buffer}),4326)) AS geom 
        FROM gtfs.stops st, tmp_study_area_buffer sa 
        WHERE ST_Intersects(st.stop_loc, sa.geom)
        """
        if study_area_ids is not None and len(study_area_ids) > 0:
            sql_query += f" AND sa.id = any(array{study_area_ids})"

    else:
        # fetch study area for walking/cycling bulk objects
        sql_query = f"""
        SELECT st_union(geom) as geom FROM basic.study_area sa 
        """
        if study_area_ids is not None and len(study_area_ids) > 0:
            sql_query += f" WHERE sa.id = any(array{study_area_ids})"

    study_area_geom = gpd.read_postgis(sql_query, legacy_engine)
    if study_area_geom.empty:
        raise Exception("No study area found")

    # - CREATE GRID FOR CALCULATION
    h3_calculation_grid = create_h3_grid(
        study_area_geom.iloc[0]["geom"],
        calculation_resolution,
        return_h3_geometries=True,
        return_h3_centroids=True,
    )

    h3_calculation_grid.to_crs(epsg=3857, inplace=True)

    # - CREATE CALCULATION OBJECTS
    calculation_objs = {}
    for row in h3_calculation_grid.itertuples():
        bulk_id = h3.h3_to_parent(row.h3_index, bulk_resolution)
        if bulk_id not in calculation_objs:
            calculation_objs[bulk_id] = {
                "lons": [],
                "lats": [],
                "coords": [],
                "calculation_ids": [],
                "starting_point_objs": [],
                "extents": [],
            }
        lat, lon = h3.h3_to_geo(row.h3_index)
        calculation_objs[bulk_id]["lons"].append(lon)
        calculation_objs[bulk_id]["lats"].append(lat)
        coords = [lon, lat]
        calculation_objs[bulk_id]["starting_point_objs"].append(
            IsochroneStartingPointCoord(lat=lat, lon=lon)
        )
        calculation_objs[bulk_id]["coords"].append(coords)
        calculation_objs[bulk_id]["calculation_ids"].append(row.h3_index)
        if bulk_obj_type == PrepareBulkObjType.TRANSIT:
            # for transit we don't know how far you can reach so the extent of the isochrone is a large safe buffer in meters
            # TODO: Find a better way to define the extent of the isochrone for transit
            extent = row.geometry.buffer(65000 * math.sqrt(2), cap_style=3)
        else:
            extent = row.geometry.buffer(starting_point_buffer * math.sqrt(2), cap_style=3)

        calculation_objs[bulk_id]["extents"].append(list(extent.bounds))

    return calculation_objs


async def compute_transit_traveltime_active_mobility(isochrone_dto: dict, calculation_objs: dict):
    # PREPARE PAYLOADS
    for bulk_idx, (bulk_id, bulk_obj) in enumerate(calculation_objs.items()):
        starting_time_section = time.time()
        print_info(
            f"Starting to compute isochrones for bulk {bulk_id} - {bulk_idx +1 } of {len(calculation_objs)}"
        )

        payloads = []
        for idx, value in enumerate(bulk_obj["calculation_ids"]):
            payload = isochrone_dto.copy()
            payload["h3_index"] = value
            payload["fromLon"] = bulk_obj["lons"][idx]
            payload["fromLat"] = bulk_obj["lats"][idx]
            extent = bulk_obj["extents"][idx]
            extent = list(web_mercator_to_wgs84(box(*extent, ccw=True)).bounds)
            payload["bounds"] = {
                "north": extent[3],
                "south": extent[1],
                "east": extent[2],
                "west": extent[0],
            }
            payloads.append(payload)
        # EXECUTE THE REQUESTS IN PARALLEL FETCH ISOCHRONES
        # bulk_size = len(calculation_objs)
        # payloads_sample = random.sample(payloads, bulk_size)
        await fetch_isochrones(
            payloads, "/app/src/cache/traveltime_matrices/public_transport", parallel_requests=60
        )
        print_info(
            f"Computed {bulk_id} isochrones in {time.time() - starting_time_section} seconds"
        )

    return None


async def fetch_isochrones(
    payloads: dict,
    save_dir: str,
    parallel_requests: int = None,
):
    start = time.time()
    if parallel_requests is None:
        parallel_requests = len(payloads)
    async with ClientSession(
        auth=BasicAuth(user, password),
    ) as client:
        for i in range(0, len(payloads), parallel_requests):
            api_calls = []
            batch = payloads[i : i + parallel_requests]
            for index, payload in enumerate(batch):
                api_calls.append(get_isochrone(payload, client))
            results = await asyncio.gather(*api_calls)
            print(f"Batch {i} done")

    print(f"Done in {time.time() - start} seconds")


async def get_isochrone(payload, client):
    data = None
    retry_count = 0
    while data is None and retry_count < 10:
        try:
            print(f"Getting isochrone for {payload['h3_index']}")
            async with client.post(settings.R5_API_URL + "/analysis", json=payload) as response:
                response.raise_for_status()
                if response.status == 202:
                    # throw exception to retry. 202 means that the request is still being processed
                    raise ClientError("Request still being processed")
                data = await response.content.read()
        except ClientError:
            # sleep a little and try again for
            print(f"Retrying {payload['h3_index']}")
            retry_count += 1
            await asyncio.sleep(3)

    if data is None:
        raise Exception(f"Could not get isochrone for {payload['h3_index']}")
    grid = decode_r5_grid(data)
    grid = filter_r5_grid(grid, 5, 60)  # TODO: Make this configurable
    h3_index = payload["h3_index"]
    payload["grid"] = grid
    return payload


async def main():
    # CREATE THE H3 GRID FOR THE STUDY AREA
    starting_point_buffer = WALKING_SPEED * MAX_WALK_TIME * 60  # in meters
    calculation_objs = await prepare_bulk_objs(
        bulk_resolution=6,
        calculation_resolution=9,
        study_area_ids=[91620000],
        bulk_obj_type=PrepareBulkObjType.TRANSIT,
        starting_point_buffer=starting_point_buffer,
    )
    await compute_transit_traveltime_active_mobility(PAYLOAD, calculation_objs)
    print("Done")
    pass


# ADD MAIN FUNCTION
if __name__ == "__main__":
    asyncio.run(main())
