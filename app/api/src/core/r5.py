import asyncio
import base64
import math
import os
import time
from enum import Enum
from pathlib import Path

import geopandas as gpd
import h3
from aiohttp import BasicAuth, ClientError, ClientSession
from pydantic import BaseModel, Field
from shapely.geometry import Point, box

from src.core.config import settings
from src.core.heatmap import save_traveltime_matrix
from src.db.session import legacy_engine
from src.utils import (
    create_h3_grid,
    decode_r5_grid,
    filter_r5_grid,
    print_info,
    print_warning,
    web_mercator_to_wgs84,
)

# ====================#
# ====== WORKER ======#
# ====================#


# -- R5 CONFIGURATION --
RESOLUTION = 9
MAX_DISTANCE_FROM_CENTER = 80000  # in meters (used to calculate the bounds from each hex center)
WALKING_SPEED = 1.39  # in m/s
MAX_WALK_TIME = 20  # in minutes
PAYLOAD_TMPL = {
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

#TODO: !! circular import ERRROR when importing from src.core.heatmap
class IsochroneStartingPointCoord(BaseModel):
    lat: float = Field(..., gt=-90, lt=90)
    lon: float = Field(..., gt=-180, lt=180)

#TODO: !! circular import ERRROR when importing from src.core.heatmap
class HeatmapMode(Enum):
    walking = "walking"
    cycking = "cycling"
    transit = "transit"

#TODO: !! circular import ERRROR when importing from src.core.heatmap
class BulkTravelTime(BaseModel):
    west: list[int]
    north: list[int]
    zoom: list[int]
    width: list[int]
    height: list[int]
    grid_ids: list[int]
    travel_times: list[list[int]]

user, password = (
    base64.b64decode(settings.R5_AUTHORIZATION.split(" ")[1]).decode("utf-8").split(":")
)


async def prepare_bulk_objs(
    bulk_resolution: int,
    calculation_resolution: int,
    study_area_ids: list[int] = None,
    bulk_obj_type: HeatmapMode = HeatmapMode.walking,
    starting_point_buffer: float = 1668,
) -> dict:

    """Creates the starting points for the traveltime matrix calculation.

    Args:
        bulk_resolution (int): H3 resolution for the bulk grids.
        calculation_resolution (int): H3 resolution for the calculation grids.
        study_area_ids (list[int], optional): List of study area ids. Defaults to None and will use all study area.
        bulk_obj_type (HeatmapMode, optional): Type of bulk object. Defaults to HeatmapMode.walking.
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

    # FETCH STUDY AREA GEOMETRY

    # Buffer size for the study area. This is computed in order to include all hex res 6 hexagon within the study area.
    # Multiplying the edge length of a hexagon with 2 will give the diameter of the hexagon.
    study_area_buffer = h3.edge_length(bulk_resolution, "m") * 2
    # TODO: Revise this hex creation if it is correct on the edges of the study area
    if bulk_obj_type == HeatmapMode.transit:
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

    # CREATE GRID FOR CALCULATION
    h3_calculation_grid = create_h3_grid(
        study_area_geom.iloc[0]["geom"],
        calculation_resolution,
        return_h3_geometries=True,
        return_h3_centroids=True,
    )

    h3_calculation_grid.to_crs(epsg=3857, inplace=True)

    # CREATE CALCULATION OBJECTS
    # TODO: This part is a bit slow when using a large study area. We should look into a faster way to create the bulk objects.
    calculation_objs = {}
    for row in h3_calculation_grid.itertuples():
        bulk_id = h3.h3_to_parent(row.h3_index, bulk_resolution)
        if bulk_id not in calculation_objs:
            calculation_objs[bulk_id] = {
                "lons": [],
                "lats": [],
                "coords": [],
                "calculation_ids": [],
                "extents": [],
            }
        lat, lon = h3.h3_to_geo(row.h3_index)
        calculation_objs[bulk_id]["lons"].append(lon)
        calculation_objs[bulk_id]["lats"].append(lat)
        coords = [lon, lat]
        # TODO: Why we do we need the IsochroneStartingPointCoord model for walking.  We have the same data in the coords list and also in lons and lats.
        if bulk_obj_type != HeatmapMode.transit:
            if "starting_point_objs" not in calculation_objs[bulk_id]:
                calculation_objs[bulk_id]["starting_point_objs"] = []
            calculation_objs[bulk_id]["starting_point_objs"].append(
                IsochroneStartingPointCoord(lat=lat, lon=lon)
            )
        calculation_objs[bulk_id]["coords"].append(coords)
        calculation_objs[bulk_id]["calculation_ids"].append(row.h3_index)
        if bulk_obj_type == HeatmapMode.transit:
            # for transit we don't know how far you can reach so the extent of the isochrone is a large safe buffer in meters
            # if we don't define the extent of the isochrone the calculation will take a very long time as R5 will calculate it for the whole project extent.
            # TODO: Find a better way to define the extent of the isochrone for transit
            extent = row.geometry.buffer(65000 * math.sqrt(2), cap_style=3)
        else:
            extent = row.geometry.buffer(starting_point_buffer * math.sqrt(2), cap_style=3)

        calculation_objs[bulk_id]["extents"].append(list(extent.bounds))

    return calculation_objs


async def process_bulk(
    bulk_id: str,
    bulk_obj: dict,
    output_dir: str,
    parallel_requests: int = None,
    upload_to_s3: bool = False,
) -> BulkTravelTime:
    start = time.time()
    print_info(f"Starting to process travel times for bulk {bulk_id}")
    # Create output dir if it does not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Prepare metadata. This will be used to create the metadata file for the bulk object to know which h3 index was calculated and which has failed.
    metadata = {"h3_index": [], "processing_time": [], "status": [], "geometry": []}
    # Prepare R5 payloads
    # Loop through all calculation objects and create a payload for each one
    payloads = []
    for idx, value in enumerate(bulk_obj["calculation_ids"]):
        payload = PAYLOAD_TMPL.copy()
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

    # Send requests to R5 API in batches
    traveltimeobjs = {
        "west": [],
        "north": [],
        "zoom": [],
        "width": [],
        "height": [],
        "grid_ids": [],
        "travel_times": [],
    }
    if parallel_requests is None:
        parallel_requests = len(payloads)
    async with ClientSession(
        auth=BasicAuth(user, password),
    ) as client:
        for i in range(0, len(payloads), parallel_requests):
            api_calls = []
            batch = payloads[i : i + parallel_requests]
            for index, payload in enumerate(batch):
                api_calls.append(
                    fetch_travel_time(
                        payload=payload,
                        client=client,
                        travel_time_percentile=5,
                        travel_time_limit=60,
                    )
                )
            results = await asyncio.gather(*api_calls)
            for result in results:
                h3_grid_id = result["h3_index"]
                grid = result["grid"]
                status = "success"
                if grid == None:
                    status = "failed"
                    continue
                traveltimeobjs["west"].append(grid["west"])
                traveltimeobjs["north"].append(grid["north"])
                traveltimeobjs["zoom"].append(grid["zoom"])
                traveltimeobjs["width"].append(grid["width"])
                traveltimeobjs["height"].append(grid["height"])
                traveltimeobjs["grid_ids"].append(h3_grid_id)
                traveltimeobjs["travel_times"].append(grid["data"])
                # fill metadata
                metadata["h3_index"].append(h3_grid_id)
                metadata["processing_time"].append(time.time())
                metadata["status"].append(status)
                metadata["geometry"].append(Point(payload["fromLon"], payload["fromLat"]))

    # Save results to npz file
    print_info(f"Saving travel times for {bulk_id}")
    save_traveltime_matrix(bulk_id=bulk_id, traveltimeobjs=traveltimeobjs, output_dir=output_dir)
    # Save metadata to geojson file
    metadata_output_dir = f"{output_dir}/metadata"
    if not os.path.exists(metadata_output_dir):
        os.makedirs(metadata_output_dir)
    metadata_gdf = gpd.GeoDataFrame(metadata, geometry="geometry", crs="EPSG:4326")
    metadata_gdf.to_file(
        Path(metadata_output_dir, f"metadata_{bulk_id}.geojson"),
        driver="GeoJSON",
    )
    # Copy to S3 bucket (if configured)
    if upload_to_s3:
        print_info(f"Uploading travel times for {bulk_id} to S3")
        # TODO
        # upload npz and metadata to S3
    print_info(f"Computed travel times for {bulk_id} in {time.time() - start} seconds")
    return traveltimeobjs


async def fetch_travel_time(
    payload: dict,
    client: ClientSession,
    travel_time_percentile: int = 5,
    travel_time_limit: int = 60,
) -> dict:
    """
    Fetches a single travel time from the R5 API and returns the decoded grid
    Grid is filtered to only include the area within the study area within the travel time surface
    """
    data = None
    retry_count = 0
    while data is None and retry_count < 15:
        try:
            async with client.post(settings.R5_API_URL + "/analysis", json=payload) as response:
                response.raise_for_status()
                if response.status == 202:
                    # throw exception to retry. 202 means that the request is still being processed
                    raise ClientError("Request still being processed")
                data = await response.content.read()
        except ClientError:
            # sleep a little and try again for
            retry_count += 1
            await asyncio.sleep(3)

    if data is None:
        print_warning(f"Could not fetch travel time for {payload['h3_index']}")
        payload["grid"] = None
        return payload
    grid = decode_r5_grid(data)
    grid = filter_r5_grid(
        grid, travel_time_percentile, travel_time_limit
    )  # todo: compare the travel time result with the one from conveyal to see if they are the same
    payload["grid"] = grid
    print_info(f"Fetched travel time for {payload['h3_index']}")
    return payload


# ====================#
# ====== TESTING =====#
# ====================#

# This methods below are only used for testing purposes.
async def compute_transit_traveltime_active_mobility(calculation_objs: dict):
    # PREPARE PAYLOADS
    for bulk_idx, (bulk_id, bulk_obj) in enumerate(calculation_objs.items()):
        print_info(f"{bulk_id} - {bulk_idx +1 } of {len(calculation_objs)}")
        await process_bulk(
            bulk_id,
            bulk_obj,
            "/app/src/cache/traveltime_matrices/public_transport",
            parallel_requests=60,
            upload_to_s3=False,
        )

    return None


async def main():
    # CREATE THE H3 GRID FOR THE STUDY AREA
    starting_point_buffer = WALKING_SPEED * MAX_WALK_TIME * 60  # in meters
    calculation_objs = await prepare_bulk_objs(
        bulk_resolution=6,
        calculation_resolution=9,
        study_area_ids=[91620000],
        bulk_obj_type=HeatmapMode.transit,
        starting_point_buffer=starting_point_buffer,
    )
    await compute_transit_traveltime_active_mobility(calculation_objs)
    print("Done")
    pass


# ADD MAIN FUNCTION
if __name__ == "__main__":
    asyncio.run(main())
