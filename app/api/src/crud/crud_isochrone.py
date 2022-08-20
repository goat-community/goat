import io
import json
import os
import shutil
import uuid
from errno import ELOOP
from typing import Any

import numpy as np
import pandas as pd
import requests
from fastapi import Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from geojson import FeatureCollection
from geopandas import GeoDataFrame, GeoSeries
from geopandas.io.sql import read_postgis
from pandas.io.sql import read_sql
from pyproj import Transformer
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
    IsochroneMultiRegionType
)
from src.utils import (
    compute_single_value_surface,
    decode_r5_grid,
    delete_dir,
    encode_r5_grid,
    group_opportunities_single_isochrone,
    group_opportunities_multi_isochrone
)


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
    async def read_network(self, db, obj_in: IsochroneDTO, current_user) -> Any:
        isochrone_type = None
        if len(obj_in.starting_point.input) == 1 and isinstance(
            obj_in.starting_point.input[0], IsochroneStartingPointCoord
        ):
            isochrone_type = IsochroneTypeEnum.single.value
        else:
            isochrone_type = IsochroneTypeEnum.multi.value

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
            routing_profile = obj_in.mode.value + "_" + obj_in.settings.walking_profile.value

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
        starting_id = edges_network.iloc[0].starting_ids
        if len(obj_in.starting_point.input) == 1:
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
        await db.refresh(obj_starting_point)

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
        return edges_network, starting_id

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

        reached_opportunities = features[0]["properties"]["reached_opportunities"].keys()
        for oportunity in reached_opportunities:
            gdf[oportunity] = str(gdf["properties"][0]["reached_opportunities"][oportunity])
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

    async def get_opportunities_multi_isochrone(self, grid_decoded, isochrone_obj, current_user) -> Any:
        """
        Get opportunities (population) for multiple isochrones
        """
        max_time = isochrone_obj.settings.travel_time 
        modus = isochrone_obj.scenario.modus.value
        scenario_id = isochrone_obj.scenario.id


        
        max_isochrone_geom = await self.get_max_isochrone_shape(grid_decoded, max_time)
        max_isochrone_wkt = max_isochrone_geom.wkt

        # isochrone_obj.scenario.region_type.value
        if 'study_area' == IsochroneMultiRegionType.STUDY_AREA.value:

            ################################################
            # TODO: Read study area ids from payload
            sub_study_area_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] 

            get_study_area_reachable_population_query = f"""
                SELECT * 
                FROM basic.reachable_population_study_area({scenario_id},'{modus}', ARRAY{sub_study_area_ids})
            """
            get_study_area_reachable_population = read_sql(
                get_study_area_reachable_population_query,
                legacy_engine,
            )

            get_population_multi_query = f"""
                SELECT * 
                FROM basic.get_population_multi_sum(
                    {current_user.id}, 
                    '{modus}', 
                    ST_GeomFromText('{max_isochrone_wkt}', 4326), 
                    ARRAY{sub_study_area_ids},
                    {grid_decoded["zoom"]},
                    {scenario_id}
                ) 
            """
            get_population_multi = read_sql(
                get_population_multi_query,
                legacy_engine,
            )

            get_population_sum_pixel = np.array(get_population_multi["pixel"].tolist())
            get_population_sum_population = get_population_multi["population"].to_numpy()
            get_population_sub_study_area_id = get_population_multi["sub_study_area_id"].to_numpy()

            amenity_grid_count = group_opportunities_multi_isochrone(
                grid_decoded["west"],
                grid_decoded["north"],
                grid_decoded["width"],
                grid_decoded["surface"],
                get_population_sum_pixel,
                get_population_sum_population,
                get_population_sub_study_area_id,
                np.array(sub_study_area_ids),
                max_time,
            )
            
            for i in amenity_grid_count[1]:
                
                # index = np.where(get_poi_one_entrance_sum_category[1] == amenity_grid_count[1][i])[0]
                # value = get_poi_one_entrance_sum["category"][index[0]]
                # amenity_count[value] = amenity_grid_count[2][i].tolist()
                print(i)


            return amenity_grid_count

    async def get_opportunities_single_isochrone(self, grid_decoded, isochrone_obj, current_user) -> Any:
        """
        Get opportunities (population+POIs) for single isochrone
        """

        max_time = isochrone_obj.settings.travel_time 
        modus = isochrone_obj.scenario.modus.value
        scenario_id = isochrone_obj.scenario.id
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
        get_aoi_query = f"""
            SELECT category, ST_AREA(geom::geography)::integer AS area, geom 
            FROM basic.aoi a 
            WHERE ST_Intersects(a.geom, ST_GeomFromText('{max_isochrone_wkt}', 4326))
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
        get_aoi = read_sql(get_aoi_query, legacy_engine)
        # TODO: Get intersection of AOI and isochrone

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
        amenity_count = {"population": amenity_grid_count[0].tolist()}
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
            obj_in_data["region_geom"] = obj_in.starting_point.region

        sql_starting_points = text(
            """SELECT x, y 
        FROM basic.starting_points_multi_isochrones(:user_id, :modus, :minutes, :speed, :amenities, :scenario_id, :active_upload_ids, :region_geom, :study_area_ids)"""
        )
        starting_points = await db.execute(sql_starting_points, obj_in_data)
        starting_points = starting_points.fetchall()
        return starting_points
    
    async def calculate(self, db: AsyncSession, obj_in: IsochroneDTO, current_user: models.User) -> Any:
        """
        Calculate the isochrone for a given location and time
        """
        result = None
        if obj_in.mode.value in [IsochroneMode.WALKING.value, IsochroneMode.CYCLING.value]:
            network, starting_ids = await self.read_network(db, obj_in, current_user)
            grid = compute_isochrone(
                network, starting_ids, obj_in.settings.travel_time, obj_in.output.resolution
            )
            # === Amenity Intersect ===#
            grid_decoded = await self.get_opportunities_multi_isochrone(
                grid, obj_in, current_user
            )
            grid_encoded = encode_r5_grid(grid)
            result = Response(bytes(grid_encoded))
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
            grid_decoded = decode_r5_grid(response.content)
            # === Amenity Intersect and Encode ===#
            grid_decoded = await self.get_opportunities_single_isochrone(grid_decoded, 120)
            grid_encoded = encode_r5_grid(grid_decoded)
            result = Response(bytes(grid_encoded))
        return result


isochrone = CRUDIsochrone()
