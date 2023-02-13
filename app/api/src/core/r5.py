import asyncio

import aiohttp
import geopandas as gpd

from src.core.config import settings
from src.db.session import legacy_engine
from src.utils import create_h3_grid

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
headers = {}
if settings.R5_AUTHORIZATION:
    headers["Authorization"] = settings.R5_AUTHORIZATION


async def get_isochrone(payload, session, save_dir):
    async with session.post(
        settings.R5_API_URL + "/analysis", json=payload, headers=headers
    ) as response:
        response_data = await response.content.read()
        h3_index = payload["h3_index"]
        if response.status == 200:
            with open(f"{save_dir}/{h3_index}.bin", "wb") as f:
                f.write(response_data)
        else:
            fromLat = payload["fromLat"]
            fromLon = payload["fromLon"]
            print(f"Request failed on hex {h3_index} with lat and lon: {fromLat}, {fromLon}")

        return response_data


async def fetch_isochrones(payloads, batch_size, save_dir):

    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = []
        for i in range(0, len(payloads), batch_size):
            batch = payloads[i : i + batch_size]
            for index, payload in enumerate(batch):
                tasks.append(get_isochrone(payload, session, save_dir))
            await asyncio.gather(*tasks)


def main():
    # CREATE THE H3 GRID FOR THE STUDY AREA
    stop_buffer = WALKING_SPEED * MAX_WALK_TIME * 60  # in meters
    study_area_ids = [91620000]
    sql_query = f"""
    SELECT st_union(st_transform(st_buffer(st_transform(st.stop_loc, 3857),{stop_buffer}),4326)) AS geom 
    FROM gtfs.stops st, basic.study_area sa 
    WHERE ST_Intersects(st.stop_loc, sa.buffer_geom_heatmap) 
    """
    if study_area_ids is not None and len(study_area_ids) > 0:
        sql_query += f" AND sa.id = any(array{study_area_ids})"

    study_area_geom = gpd.read_postgis(sql_query, legacy_engine)
    if study_area_geom.empty:
        raise Exception("No study area found")
    study_area_h3_grid = create_h3_grid(
        study_area_geom.iloc[0]["geom"],
        RESOLUTION,
        return_h3_geometries=True,
        return_h3_centroids=True,
    )
    study_area_h3_grid.to_crs(epsg=3857, inplace=True)
    # calculate bounds for each hexagon in meter for a specified distance and add to dataframe
    study_area_h3_grid["extent"] = study_area_h3_grid["geometry"].buffer(MAX_DISTANCE_FROM_CENTER)
    study_area_h3_grid.to_crs(epsg=4326, inplace=True)
    study_area_h3_grid.set_geometry("extent", inplace=True, crs=3857)
    study_area_h3_grid.to_crs(epsg=4326, inplace=True)
    study_area_h3_grid.set_geometry("geometry", inplace=True, crs=4326)

    # CREATE THE PAYLOADS
    payloads = []
    for _, row in study_area_h3_grid.iterrows():
        payload = PAYLOAD.copy()
        bounds = row["extent"].bounds
        payload["h3_index"] = row["h3_index"]
        payload["fromLon"] = row["geometry"].x
        payload["fromLat"] = row["geometry"].y
        payload["bounds"] = {
            "north": bounds[3],
            "south": bounds[1],
            "east": bounds[2],
            "west": bounds[0],
        }
        payloads.append(payload)

    # EXECUTE THE REQUESTS IN PARALLEL FETCH ISOCHRONES
    bulk_size = 10
    asyncio.run(
        fetch_isochrones(
            payloads[:bulk_size], bulk_size, "/app/src/cache/traveltime_matrices/public_transport"
        )
    )

    pass


# ADD MAIN FUNCTION
if __name__ == "__main__":
    main()
