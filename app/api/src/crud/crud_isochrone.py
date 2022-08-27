import io
import json
import math
import os
import shutil
import time
import uuid
from errno import ELOOP
from typing import Any
from unicodedata import category

import matplotlib.path
import numpy as np
import pandas as pd
import pyproj
import requests
from fastapi import Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from geojson import FeatureCollection
from geopandas import GeoDataFrame, GeoSeries
from geopandas.io.sql import read_postgis
from pandas.io.sql import read_sql
from pyproj import Transformer
from shapely import wkt
from shapely.geometry import MultiPolygon, Point, Polygon, shape
from shapely.ops import unary_union
from sqlalchemy import intersect
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import text
from urllib3 import HTTPResponse

from src.core.config import settings
from src.core.isochrone import compute_isochrone
from src.crud.base import CRUDBase
from src.db import models
from src.db.session import legacy_engine
from src.exts.cpp.bind import isochrone as isochrone_cpp
from src.jsoline import jsolines
from src.resources.enums import IsochroneExportType, IsochroneTypes
from src.schemas.isochrone import (
    IsochroneDTO,
    IsochroneMode,
    IsochroneMulti,
    IsochroneMultiRegionType,
    IsochroneSingle,
    IsochroneStartingPointCoord,
    IsochroneTypeEnum,
)
from src.utils import (
    compute_single_value_surface,
    decode_r5_grid,
    delete_dir,
    encode_r5_grid,
    geometry_to_pixel,
    group_opportunities_multi_isochrone,
    group_opportunities_single_isochrone,
    web_mercator_to_wgs84,
    wgs84_to_web_mercator,
)

web_mercator_proj = pyproj.Proj("EPSG:3857")


class CRUDIsochroneCalculation(
    CRUDBase[models.IsochroneCalculation, models.IsochroneCalculation, models.IsochroneCalculation]
):
    pass


isochrone_calculation = CRUDIsochroneCalculation(models.IsochroneCalculation)


class CRUDIsochroneFeature(
    CRUDBase[models.IsochroneFeature, models.IsochroneFeature, models.IsochroneFeature]
):
    pass


isochrone_feature = CRUDIsochroneCalculation(models.IsochroneFeature)


class CRUDIsochrone:
    async def read_network(self, db, obj_in: IsochroneDTO, current_user, isochrone_type) -> Any:

        sql_text = ""
        if isochrone_type == IsochroneTypeEnum.single.value:
            sql_text = f"""SELECT id, source, target, cost, reverse_cost, coordinates_3857 as geom, length_3857 AS length, starting_ids, starting_geoms
            FROM basic.fetch_network_routing(ARRAY[:x],ARRAY[:y], :max_cutoff, :speed, :modus, :scenario_id, :routing_profile)
            """
        elif isochrone_type == IsochroneTypeEnum.multi.value:
            sql_text = f"""SELECT id, source, target, cost, reverse_cost, coordinates_3857 as geom, length_3857 AS length, starting_ids, starting_geoms
            FROM basic.fetch_network_routing_multi(:x,:y, :max_cutoff, :speed, :modus, :scenario_id, :routing_profile)
            """
        # elif calculation_type == IsochroneTypeEnum.heatmap:
        #     sql_text = f"""SELECT id, source, target, cost, reverse_cost, coordinates_3857 as geom, length_3857 AS length, starting_ids, starting_geoms
        #     FROM basic.fetch_network_routing_heatmap(:x,:y, :max_cutoff, :speed, :modus, :scenario_id, :routing_profile)
        #     """

        read_network_sql = text(sql_text)
        routing_profile = None
        if obj_in.mode.value == IsochroneMode.WALKING.value:
            routing_profile = obj_in.mode.value + "_" + obj_in.settings.walking_profile.value

        if obj_in.mode.value == IsochroneMode.CYCLING.value:
            routing_profile = obj_in.mode.value + "_" + obj_in.settings.cycling_profile.value

        x = y = None
        if isochrone_type == IsochroneTypeEnum.multi.value:
            if isinstance(obj_in.starting_point.input[0], IsochroneStartingPointCoord):
                x = [point.lon for point in obj_in.startiong_point.input]
                y = [point.lat for point in obj_in.startiong_point.input]
            else:
                starting_points = await self.starting_points_opportunities(
                    current_user, db, obj_in
                )
                x = starting_points[0][0]
                y = starting_points[0][1]
        else:
            x = obj_in.starting_point.input[0].lon
            y = obj_in.starting_point.input[0].lat

        edges_network = read_sql(
            read_network_sql,
            legacy_engine,
            params={
                "x": x,
                "y": y,
                "max_cutoff": obj_in.settings.travel_time * 60,  # in seconds
                "speed": obj_in.settings.speed,
                "modus": obj_in.scenario.modus.value,
                "scenario_id": obj_in.scenario.id,
                "routing_profile": routing_profile,
            },
        )
        starting_ids = edges_network.iloc[0].starting_ids
        if len(obj_in.starting_point.input) == 1 and isinstance(
            obj_in.starting_point.input[0], IsochroneStartingPointCoord
        ):
            starting_point_geom = str(
                GeoDataFrame(
                    {"geometry": Point(edges_network.iloc[-1:]["geom"].values[0][0])},
                    crs="EPSG:3857",
                    index=[0],
                )
                .to_crs("EPSG:4326")
                .to_wkt()["geometry"]
                .iloc[0]
            )
        else:
            starting_point_geom = str(edges_network["starting_geoms"].iloc[0])

        edges_network = edges_network.drop(["starting_ids", "starting_geoms"], axis=1)
        obj_starting_point = models.IsochroneCalculation(
            calculation_type=isochrone_type,
            user_id=current_user.id,
            scenario_id=None if obj_in.scenario.id == 0 else obj_in.scenario.id,
            starting_point=starting_point_geom,
            routing_profile=routing_profile,
            speed=obj_in.settings.speed * 3.6,  # in km/h
            modus=obj_in.scenario.modus.value,
            parent_id=None,
        )

        db.add(obj_starting_point)
        await db.commit()

        # return edges_network and obj_starting_point
        edges_network.astype(
            {
                "id": np.int64,
                "source": np.int64,
                "target": np.int64,
                "cost": np.double,
                "reverse_cost": np.double,
                "length": np.double,
            }
        )
        return edges_network, starting_ids

    async def export_isochrone(
        self,
        db: AsyncSession,
        *,
        current_user,
        return_type,
        geojson_dictionary: dict,
    ) -> Any:

        features = geojson_dictionary["features"]
        # Remove the payload and set to true to use it later
        geojson_dictionary = True
        for _data in features:
            # Shape the geometries
            _data["geometry"] = shape(_data["geometry"])
        gdf = GeoDataFrame(features).set_geometry("geometry")
        # Translate the properties to columns
        properties = list(features[0]["properties"].keys())
        properties.remove("reached_opportunities")
        for property_ in properties:
            gdf[property_] = str(gdf["properties"][0][property_])

        reached_opportunities = features[0]["properties"]["reached_opportunities"]
        for oportunity in reached_opportunities.keys():
            if type(reached_opportunities[oportunity]) is dict:
                for key in reached_opportunities[oportunity].keys():
                    gdf[key] = reached_opportunities[oportunity][key]
            else:
                gdf[oportunity] = str(reached_opportunities[oportunity])

        gdf = gdf.drop(["properties"], axis=1)
        # Preliminary fix for tranlation POIs categories
        ########################################################################################################################
        if current_user.language_preference == "de":
            with open("/app/src/resources/poi_de.json") as json_file:
                translation_dict = json.load(json_file)
        else:
            with open("/app/src/resources/poi_en.json") as json_file:
                translation_dict = json.load(json_file)
        updated_columns = []
        for column in gdf.columns:
            if column in translation_dict:
                updated_columns.append(translation_dict[column])
            else:
                updated_columns.append(column)
        gdf.columns = updated_columns
        ########################################################################################################################

        defined_uuid = uuid.uuid4().hex
        file_name = "isochrone_export"
        file_dir = f"/tmp/{defined_uuid}"

        os.makedirs(file_dir + "/export")
        os.chdir(file_dir + "/export")

        if return_type == IsochroneExportType.geojson:
            gdf.to_file(
                file_name + "." + IsochroneExportType.geojson.name,
                driver=IsochroneExportType.geojson.value,
            )
        elif return_type == IsochroneExportType.shp:
            gdf.to_file(
                file_name + "." + IsochroneExportType.shp.name,
                driver=IsochroneExportType.shp.value,
                encoding="utf-8",
            )
        elif return_type == IsochroneExportType.xlsx:
            gdf = gdf.drop(["geometry"], axis=1)
            writer = pd.ExcelWriter(
                file_name + "." + IsochroneExportType.xlsx.name, engine="xlsxwriter"
            )
            gdf_transposed = gdf.transpose()
            gdf_transposed.columns = [
                translation_dict["attributes"] for c in list(gdf[translation_dict["traveltime"]])
            ]
            gdf_transposed[1:].to_excel(writer, sheet_name="Results")
            workbook = writer.book
            worksheet = writer.sheets["Results"]
            worksheet.set_column(0, 0, 35, None)
            worksheet.set_column(1, gdf.shape[0], 25, None)
            writer.save()

        os.chdir(file_dir)
        shutil.make_archive(file_name, "zip", file_dir + "/export")

        with open(file_name + ".zip", "rb") as f:
            data = f.read()

        delete_dir(file_dir)
        response = StreamingResponse(io.BytesIO(data), media_type="application/zip")
        response.headers["Content-Disposition"] = "attachment; filename={}".format(
            file_name + ".zip"
        )
        return response

    async def get_max_isochrone_shape(self, grid_decoded, max_time):
        """
        Gets the isochrone with the highest travel time for opportunity intersect.
        """
        single_value_surface = compute_single_value_surface(
            grid_decoded["width"],
            grid_decoded["height"],
            grid_decoded["depth"],
            grid_decoded["data"],
            50,
        )
        grid_decoded["surface"] = single_value_surface
        isochrone_multipolygon_coordinates = jsolines(
            grid_decoded["surface"],
            grid_decoded["width"],
            grid_decoded["height"],
            grid_decoded["west"],
            grid_decoded["north"],
            grid_decoded["zoom"],
            max_time,
        )
        multipolygon_shape = shape(
            {"type": "MultiPolygon", "coordinates": isochrone_multipolygon_coordinates}
        )
        return multipolygon_shape

    async def get_opportunities_multi_isochrone(self, grid_decoded, obj_in, current_user) -> Any:
        """
        Get opportunities (population) for multiple isochrones
        """
        max_time = obj_in.settings.travel_time
        modus = obj_in.scenario.modus.value
        scenario_id = obj_in.scenario.id

        clip_population_geom = await self.get_max_isochrone_shape(grid_decoded, max_time)
        if obj_in.starting_point.region_type == IsochroneMultiRegionType.STUDY_AREA:
            # Use study area ids to get reachable population
            clip_population_wkt = clip_population_geom.wkt
            sub_study_area_ids = [int(i) for i in obj_in.starting_point.region]
            get_reachable_population_query = f"""
                SELECT * 
                FROM basic.reachable_population_study_area({scenario_id}, '{modus}', ARRAY{sub_study_area_ids})
            """
            get_reachable_population = read_sql(
                get_reachable_population_query,
                legacy_engine,
            )
            sub_study_area_ids = get_reachable_population["sub_study_area_id"]

        elif obj_in.starting_point.region_type == IsochroneMultiRegionType.DRAW:
            # Get intersecting study_area_ids to pass to population reader
            clip_population_wkt = obj_in.starting_point.region[0]
            get_relevant_study_area_ids_query = f"""
                SELECT DISTINCT id AS sub_study_area_id
                FROM basic.sub_study_area
                WHERE ST_Intersects(geom, ST_GeomFromText('{clip_population_wkt}', 4326))
            """
            get_relevant_study_area_ids = read_sql(
                get_relevant_study_area_ids_query, legacy_engine
            )
            sub_study_area_ids = np.array(
                [int(i) for i in get_relevant_study_area_ids["sub_study_area_id"]]
            )
            # Use polygon to get reachable population
            get_reachable_population_query = f"""
                SELECT 1 AS sub_study_area_id, * 
                FROM basic.reachable_population_polygon({scenario_id}, '{modus}', '{clip_population_wkt}')
            """
            get_reachable_population = read_sql(
                get_reachable_population_query,
                legacy_engine,
            )

        get_population_multi_query = f"""
            SELECT * 
            FROM basic.get_population_multi_sum(
                {current_user.id}, 
                '{modus}', 
                ST_GeomFromText('{clip_population_wkt}', 4326), 
                ARRAY{sub_study_area_ids.tolist()},
                {grid_decoded["zoom"]},
                {scenario_id}
            ) 
        """
        # Read relevant population from database
        get_population_multi = read_sql(
            get_population_multi_query,
            legacy_engine,
        )

        get_population_sum_pixel = np.array(get_population_multi["pixel"].tolist())
        get_population_sum_population = get_population_multi["population"].to_numpy()
        get_population_sub_study_area_id = get_population_multi["sub_study_area_id"].to_numpy()

        # Count population for each sub_study_area_id/polygon
        population_grid_count = group_opportunities_multi_isochrone(
            grid_decoded["west"],
            grid_decoded["north"],
            grid_decoded["width"],
            grid_decoded["surface"],
            get_population_sum_pixel,
            get_population_sum_population,
            get_population_sub_study_area_id,
            sub_study_area_ids.tolist(),
            max_time,
        )
        population_count = {}

        # Bring into correct format for client
        if obj_in.starting_point.region_type == IsochroneMultiRegionType.STUDY_AREA:
            for idx, sub_study_area in get_reachable_population.iterrows():
                population_count[sub_study_area["name"]] = {
                    "total_population": sub_study_area["population"],
                    "reached_population": population_grid_count[idx].astype(int).tolist(),
                }
        elif obj_in.starting_point.region_type == IsochroneMultiRegionType.DRAW:
            reached_population = np.zeros(max_time)
            for idx, sub_study_area_id in enumerate(sub_study_area_ids):
                reached_population += population_grid_count[idx]

            population_count["polygon"] = {
                "total_population": int(get_reachable_population["population"][0]),
                "reached_population": reached_population.astype(int).tolist(),
            }

        # Add population count to grid decoded
        grid_decoded["accessibility"] = population_count

        return grid_decoded

    async def get_opportunities_single_isochrone(self, grid_decoded, obj_in, current_user) -> Any:
        """
        Get opportunities (population+POIs) for single isochrone
        """

        max_time = obj_in.settings.travel_time
        modus = obj_in.scenario.modus.value
        scenario_id = obj_in.scenario.id
        active_data_upload_ids = current_user.active_data_upload_ids
        max_isochrone_geom = await self.get_max_isochrone_shape(grid_decoded, max_time)
        max_isochrone_wkt = max_isochrone_geom.wkt

        get_population_sum_query = f"""
            SELECT * 
            FROM basic.get_population_sum(
                {current_user.id}, 
                '{modus}', 
                ST_GeomFromText('{max_isochrone_wkt}', 4326), 
                {grid_decoded["zoom"]},
                {scenario_id}
        )"""
        get_poi_one_entrance_sum_query = f"""
            SELECT * 
            FROM basic.get_poi_one_entrance_sum(
                {current_user.id}, 
                '{modus}', 
                ST_GeomFromText('{max_isochrone_wkt}', 4326), 
                {grid_decoded["zoom"]},
                {scenario_id},
                ARRAY{active_data_upload_ids}
            )
        """
        get_poi_more_entrance_sum_query = f"""
            SELECT * 
            FROM basic.get_poi_more_entrance_sum(
                {current_user.id}, 
                '{modus}', 
                ST_GeomFromText('{max_isochrone_wkt}', 4326), 
                {grid_decoded["zoom"]},
                {scenario_id},
                ARRAY{active_data_upload_ids}
            )
        """

        get_population_sum = read_sql(
            get_population_sum_query,
            legacy_engine,
        )
        get_poi_one_entrance_sum = read_sql(
            get_poi_one_entrance_sum_query,
            legacy_engine,
        )
        get_poi_more_entrance_sum = read_sql(
            get_poi_more_entrance_sum_query,
            legacy_engine,
        )

        ##-- FIND AMENITY COUNT FOR EACH GRID CELL --##
        get_population_sum_pixel = np.array(get_population_sum["pixel"].tolist())
        get_population_sum_population = get_population_sum["population"].to_numpy()
        get_poi_one_entrance_sum_pixel = np.array(get_poi_one_entrance_sum["pixel"].tolist())
        get_poi_one_entrance_sum_category = np.unique(
            get_poi_one_entrance_sum["category"], return_inverse=True
        )
        get_poi_one_entrance_sum_cnt = get_poi_one_entrance_sum["cnt"].to_numpy()
        get_poi_more_entrance_sum_pixel = np.array(get_poi_more_entrance_sum["pixel"].tolist())
        get_poi_more_entrance_sum_category = np.unique(
            get_poi_more_entrance_sum["category"], return_inverse=True
        )
        # fill null values with a string to avoid errors
        get_poi_more_entrance_sum["name"].fillna("_", inplace=True)
        get_poi_more_entrance_sum_name = np.unique(
            get_poi_more_entrance_sum["name"], return_inverse=True
        )
        get_poi_more_entrance_sum_cnt = get_poi_more_entrance_sum["cnt"].to_numpy()
        amenity_grid_count = group_opportunities_single_isochrone(
            grid_decoded["west"],
            grid_decoded["north"],
            grid_decoded["width"],
            grid_decoded["surface"],
            get_population_sum_pixel,
            get_population_sum_population,
            get_poi_one_entrance_sum_pixel,
            get_poi_one_entrance_sum_category[1],
            get_poi_one_entrance_sum_cnt,
            get_poi_more_entrance_sum_pixel,
            get_poi_more_entrance_sum_category[1],
            get_poi_more_entrance_sum_name[1],
            get_poi_more_entrance_sum_cnt,
            max_time,
        )
        amenity_count = {"population": amenity_grid_count[0].astype(int).tolist()}
        # poi one entrance
        for i in amenity_grid_count[1]:
            index = np.where(get_poi_one_entrance_sum_category[1] == amenity_grid_count[1][i])[0]
            value = get_poi_one_entrance_sum["category"][index[0]]
            amenity_count[value] = amenity_grid_count[2][i].tolist()
        # poi more entrances
        for i in amenity_grid_count[3]:
            index = np.where(get_poi_more_entrance_sum_category[1] == amenity_grid_count[3][i])[0]
            value = get_poi_more_entrance_sum["category"][index[0]]
            amenity_count[value] = amenity_grid_count[4][i].tolist()
        # aoi count
        if obj_in.mode.value not in [IsochroneMode.TRANSIT.value, IsochroneMode.CAR.value]:
            # TODO: fix performance for public transport
            get_aoi_query = f"""
                SELECT category, ST_AREA(d.geom::geography)::integer AS area, ST_AsText(ST_Transform(d.geom,3857)) as geom
                FROM basic.aoi a, LATERAL ST_DUMP(a.geom) d
                WHERE ST_Intersects(a.geom, ST_GeomFromText('{max_isochrone_wkt}', 4326))
            """
            get_aoi = read_sql(get_aoi_query, legacy_engine)
            aoi_categories = {}
            for idx, aoi in get_aoi.iterrows():
                geom = aoi["geom"]
                category = aoi["category"]
                geom_shapely = wkt.loads(geom)
                # add category to aoi_categories if not already in there
                if category not in aoi_categories:
                    aoi_categories[category] = []
                aoi_categories[category].append(geom_shapely)
            # loop through aoi_categories
            for category, polygons in aoi_categories.items():
                multipolygon = MultiPolygon(polygons)
                first_coordinate = web_mercator_to_wgs84(
                    Point(
                        multipolygon.geoms[0].exterior.coords.xy[0][0],
                        multipolygon.geoms[0].exterior.coords.xy[1][0],
                    )
                )
                scale_factor = web_mercator_proj.get_factors(
                    first_coordinate.x, first_coordinate.y, errcheck=True
                ).areal_scale

                aoi_categories[category] = {"geom": multipolygon, "scale_factor": scale_factor}

            for current_time in range(max_time):
                isochrone_shape = await self.get_max_isochrone_shape(
                    grid_decoded, current_time + 1
                )
                isochrone_polygon = wgs84_to_web_mercator(isochrone_shape)
                for category, aoi in aoi_categories.items():
                    aoi_geom = aoi["geom"]
                    aoi_scale_factor = aoi["scale_factor"]
                    category_area_diff = aoi_geom.difference(isochrone_polygon).area
                    category_area = aoi_geom.area - category_area_diff
                    if category not in amenity_count:
                        amenity_count[category] = [0] * max_time
                    amenity_count[category][current_time] = category_area / aoi_scale_factor

        ##-- ADD AMENITY TO GRID DECODED --##
        grid_decoded["accessibility"] = amenity_count

        return grid_decoded

    async def count_opportunity(self, db: AsyncSession, *, obj_in) -> dict:
        """
        Count opportunities for each study area or geometry
        """
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data["speed"] = obj_in_data["speed"] / 3.6
        sql = text(
            """SELECT count_pois
            FROM basic.count_pois_multi_isochrones(:user_id,:modus,:minutes,:speed,:region_type,:region,:amenities,:scenario_id,:active_upload_ids)"""
        )
        result = await db.execute(sql, obj_in_data)
        return result.fetchall()[0][0]

    async def starting_points_opportunities(
        self, current_user, db: AsyncSession, obj_in: IsochroneDTO
    ) -> Any:
        obj_in_data = {
            "user_id": current_user.id,
            "modus": obj_in.scenario.modus.value,
            "minutes": obj_in.settings.travel_time,
            "speed": obj_in.settings.speed,
            "amenities": obj_in.starting_point.input,
            "scenario_id": obj_in.scenario.id,
            "active_upload_ids": current_user.active_data_upload_ids,
            "region_geom": None,
            "study_area_ids": None,
        }
        if obj_in.starting_point.region_type.value == IsochroneMultiRegionType.STUDY_AREA.value:
            obj_in_data["study_area_ids"] = [
                int(study_area_id) for study_area_id in obj_in.starting_point.region
            ]
        elif obj_in.starting_point.region_type.value == IsochroneMultiRegionType.DRAW.value:
            obj_in_data["region_geom"] = obj_in.starting_point.region[0]

        sql_starting_points = text(
            """SELECT x, y 
            FROM basic.starting_points_multi_isochrones(:user_id, :modus, :minutes, :speed, :amenities, :scenario_id, :active_upload_ids, :region_geom, :study_area_ids)"""
        )
        starting_points = await db.execute(sql_starting_points, obj_in_data)
        starting_points = starting_points.fetchall()
        return starting_points

    async def calculate(
        self, db: AsyncSession, obj_in: IsochroneDTO, current_user: models.User
    ) -> Any:
        """
        Calculate the isochrone for a given location and time
        """
        grid = None
        result = None
        if len(obj_in.starting_point.input) == 1 and isinstance(
            obj_in.starting_point.input[0], IsochroneStartingPointCoord
        ):
            isochrone_type = IsochroneTypeEnum.single.value
        else:
            isochrone_type = IsochroneTypeEnum.multi.value

        # == Walking and cycling isochrone ==
        if obj_in.mode.value in [IsochroneMode.WALKING.value, IsochroneMode.CYCLING.value]:
            network, starting_ids = await self.read_network(
                db, obj_in, current_user, isochrone_type
            )
            grid = compute_isochrone(
                network, starting_ids, obj_in.settings.travel_time, obj_in.output.resolution
            )
        # == Public transport isochrone ==
        else:
            payload = {
                "accessModes": obj_in.settings.access_mode.value.upper(),
                "transitModes": ",".join(x.value.upper() for x in obj_in.settings.transit_modes),
                "bikeSpeed": obj_in.settings.bike_speed,
                "walkSpeed": obj_in.settings.walk_speed,
                "bikeTrafficStress": obj_in.settings.bike_traffic_stress,
                "date": obj_in.settings.departure_date,
                "fromTime": obj_in.settings.from_time,
                "toTime": obj_in.settings.to_time,
                "maxTripDurationMinutes": obj_in.settings.travel_time,  # TODO: Fix this
                "decayFunction": obj_in.settings.decay_function,
                "destinationPointSetIds": [],
                "directModes": obj_in.settings.access_mode.value.upper(),
                "egressModes": obj_in.settings.egress_mode.value.upper(),
                "fromLat": obj_in.starting_point.input[0].lat,
                "fromLon": obj_in.starting_point.input[0].lon,
                "zoom": obj_in.output.resolution,
                "maxBikeTime": obj_in.settings.max_bike_time,
                "maxRides": obj_in.settings.max_rides,
                "maxWalkTime": obj_in.settings.max_walk_time,
                "monteCarloDraws": obj_in.settings.monte_carlo_draws,
                "percentiles": obj_in.settings.percentiles,
                "variantIndex": -1,
                "workerVersion": "v6.4",
            }
            # TODO: Get the project id and bbox from study area.
            payload["projectId"] = "6294f0ae0cfee1c6747d696c"
            payload["bounds"] = {
                "north": 48.2905,
                "south": 47.99727,
                "east": 11.94489,
                "west": 11.31592,
            }
            response = requests.post(
                settings.R5_API_URL + "/analysis",
                json=payload,
            )
            grid = decode_r5_grid(response.content)

        # Opportunity intersect
        if isochrone_type == IsochroneTypeEnum.single.value:
            grid = await self.get_opportunities_single_isochrone(grid, obj_in, current_user)
        elif isochrone_type == IsochroneTypeEnum.multi.value:
            grid = await self.get_opportunities_multi_isochrone(grid, obj_in, current_user)

        grid_encoded = encode_r5_grid(grid)
        result = Response(bytes(grid_encoded))
        return result


isochrone = CRUDIsochrone()
