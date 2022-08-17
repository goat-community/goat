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
    IsochroneSingle,
    IsochroneTypeEnum,
)
from src.utils import (
    amenity_r5_grid_intersect,
    compute_single_value_surface,
    decode_r5_grid,
    delete_dir,
    encode_r5_grid,
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
    async def read_network(self, db, calculation_type, obj_in, obj_in_data):

        if calculation_type == IsochroneTypeEnum.single:
            sql_text = f"""SELECT id, source, target, cost, reverse_cost, coordinates_3857 as geom, length_3857 AS length, starting_ids, starting_geoms
            FROM basic.fetch_network_routing(ARRAY[:x],ARRAY[:y], :max_cutoff, :speed, :modus, :scenario_id, :routing_profile)
            """
        elif calculation_type == IsochroneTypeEnum.multi:
            sql_text = f"""SELECT id, source, target, cost, reverse_cost, coordinates_3857 as geom, length_3857 AS length, starting_ids, starting_geoms
            FROM basic.fetch_network_routing_multi(:x,:y, :max_cutoff, :speed, :modus, :scenario_id, :routing_profile)
            """
        elif calculation_type == IsochroneTypeEnum.heatmap:
            sql_text = f"""SELECT id, source, target, cost, reverse_cost, coordinates_3857 as geom, length_3857 AS length, starting_ids, starting_geoms
            FROM basic.fetch_network_routing_heatmap(:x,:y, :max_cutoff, :speed, :modus, :scenario_id, :routing_profile)
            """
        else:
            raise Exception("Unknown calculation type")

        read_network_sql = text(sql_text)

        edges_network = read_sql(read_network_sql, legacy_engine, params=obj_in_data)
        starting_id = edges_network.iloc[0].starting_ids

        # There was an issue when removing the first row (which only contains the starting point) from the edges. So it was kept.
        distance_limits = list(
            range(
                obj_in.max_cutoff // obj_in.n, obj_in.max_cutoff + 1, obj_in.max_cutoff // obj_in.n
            )
        )

        if calculation_type == IsochroneTypeEnum.single:
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

        if (
            calculation_type == IsochroneTypeEnum.single
            or calculation_type == IsochroneTypeEnum.multi
        ):
            obj_starting_point = models.IsochroneCalculation(
                calculation_type=calculation_type,
                user_id=obj_in.user_id,
                scenario_id=None if obj_in.scenario_id == 0 else obj_in.scenario_id,
                starting_point=starting_point_geom,
                routing_profile=obj_in.routing_profile,
                speed=obj_in.speed,
                modus=obj_in.modus,
                parent_id=None,
            )

            db.add(obj_starting_point)
            await db.commit()
            await db.refresh(obj_starting_point)
        else:
            obj_starting_point = None  # Heatmap

        return edges_network, starting_id, distance_limits, obj_starting_point

    def result_to_gdf(
        self,
        result,
        starting_id,
        isochrone_type: IsochroneTypes = IsochroneTypes.single,
        add_to_db=True,
    ):
        # Prepare if a single isochrone
        if isochrone_type == IsochroneTypes.single:
            isochrones = {}
            for isochrone_result in result.isochrone:
                for step in sorted(isochrone_result.shape):
                    if list(isochrones.keys()) == []:
                        isochrones[step] = GeoSeries(Polygon(isochrone_result.shape[step]))
                    else:
                        isochrones[step] = GeoSeries(
                            isochrones[previous_step].union(Polygon(isochrone_result.shape[step]))
                        )
                    previous_step = step

            for step in isochrones:
                isochrones[step] = isochrones[step].unary_union

        # Prepare if a Multi-Isochrone
        elif isochrone_type == IsochroneTypes.multi:
            isochrones = {}
            steps = sorted(result.isochrone[0].shape.keys())

            for isochrone_result in result.isochrone:
                for step in steps:
                    iso = isochrone_result.shape.get(step)
                    if iso is not None and len(iso) >= 3:
                        if step not in isochrones:
                            isochrones[step] = [Polygon(isochrone_result.shape[step])]
                        else:
                            isochrones[step].append(Polygon(isochrone_result.shape[step]))

            union_isochrones = {}
            for step in isochrones:
                if list(union_isochrones.keys()) == []:
                    union_isochrones[step] = unary_union(isochrones[step])
                else:
                    union_isochrones[step] = unary_union(
                        [unary_union(isochrones[step]), union_isochrones[previous_step]]
                    )
                previous_step = step

            isochrones = union_isochrones

        isochrones_multipolygon = {}
        for step in isochrones.keys():
            if isochrones[step].type == "Polygon":
                isochrones_multipolygon[step] = MultiPolygon([isochrones[step]])
            elif isochrones[step].type == "MultiPolygon":
                isochrones_multipolygon[step] = MultiPolygon(isochrones[step])
            else:
                raise Exception("Not correct geom type")

        isochrone_gdf = GeoDataFrame(
            {
                "step": list(isochrones_multipolygon.keys()),
                "geometry": GeoSeries(isochrones_multipolygon.values()).set_crs("EPSG:3857"),
                "isochrone_calculation_id": [starting_id] * len(isochrones),
            }
        ).to_crs("EPSG:4326")

        isochrone_gdf.rename_geometry("geom", inplace=True)

        if add_to_db == True:
            isochrone_gdf.to_postgis(
                name="isochrone_feature", con=legacy_engine, schema="customer", if_exists="append"
            )

        return isochrone_gdf

    async def compute_isochrone(self, db: AsyncSession, *, obj_in, return_network=False):
        obj_in_data = jsonable_encoder(obj_in)
        edges_network, starting_id, distance_limits, obj_starting_point = await self.read_network(
            db, IsochroneTypeEnum.single.value, obj_in, obj_in_data
        )

        obj_in_data["starting_point_id"] = obj_starting_point.id

        # Convert the isochrones result to a geodataframe and save isochrone_feature to postgis
        result = isochrone_cpp(edges_network, starting_id, distance_limits)
        isochrone_gdf = self.result_to_gdf(result, obj_starting_point.id)

        # Compute reached opportunities
        sql = text(
            """SELECT * FROM basic.thematic_data_sum(:user_id,:starting_point_id,:modus,:scenario_id,:active_upload_ids) ORDER BY isochrone_feature_step"""
        )
        result_opportunities = await db.execute(sql, obj_in_data)
        result_opportunities = result_opportunities.all()
        dict_opportunities = {}
        [dict_opportunities.update({row[1]: row[2]}) for row in result_opportunities]
        dict_ids = {}
        [dict_ids.update({row[1]: row[0]}) for row in result_opportunities]
        await db.commit()

        # Update isochrones with reached opportunities
        isochrone_gdf["id"] = isochrone_gdf["step"].map(dict_ids)
        isochrone_gdf["reached_opportunities"] = isochrone_gdf["step"].map(dict_opportunities)
        isochrone_gdf["routing_profile"] = obj_in.routing_profile
        isochrone_gdf["scenario_id"] = obj_in.scenario_id
        isochrone_gdf["modus"] = obj_in.modus

        return_obj = {"isochrones": isochrone_gdf}

        if return_network == True:
            features = []
            transformer = Transformer.from_crs(3857, 4326, always_xy=True)
            for edge in result.network:
                coords = []
                for i in edge.shape:
                    coords.append(transformer.transform(i[0], i[1]))
                feature = {
                    "geometry": {"type": "LineString", "coordinates": coords},
                    "type": "Feature",
                    "properties": {
                        "edge_id": edge.edge,
                        "isochrone_calculation_id": obj_starting_point.id,
                        "cost": max(edge.start_cost, edge.end_cost),
                        "start_cost": edge.start_cost,
                        "end_cost": edge.end_cost,
                        "start_perc": edge.start_perc,
                        "end_perc": edge.end_perc,
                        "routing_profile": obj_in.routing_profile,
                        "scenario_id": obj_in.scenario_id,
                        "modus": obj_in.modus,
                    },
                }
                features.append(feature)

            network_feature_collection = {"type": "FeatureCollection", "features": features}

            return_obj["network"] = network_feature_collection

        return return_obj

    async def compute_multi_isochrone(
        self, db: AsyncSession, *, obj_in, return_network=False
    ) -> GeoDataFrame:
        obj_in_data = jsonable_encoder(obj_in)
        edges_network, starting_id, distance_limits, obj_starting_point = await self.read_network(
            db, IsochroneTypeEnum.multi.value, obj_in, obj_in_data
        )
        obj_in_data["starting_point_id"] = starting_id

        result = isochrone_cpp(edges_network, starting_id, distance_limits)
        isochrone_gdf = self.result_to_gdf(result, obj_starting_point.id, isochrone_type="multi")

        return isochrone_gdf

    async def calculate_single_isochrone(self, db: AsyncSession, *, obj_in) -> GeoDataFrame:

        obj_in.speed = obj_in.speed / 3.6
        if obj_in.modus == "default" or obj_in.modus == "scenario":
            result = await self.compute_isochrone(db, obj_in=obj_in, return_network=False)
            result = result["isochrones"]
        elif obj_in.modus == "comparison":
            # Compute default isochrones
            obj_in_default = obj_in
            obj_in_default.modus = "default"
            isochrones_default = await self.compute_isochrone(
                db, obj_in=obj_in_default, return_network=False
            )
            # Compute scenario isochrones
            obj_in_scenario = obj_in
            obj_in_scenario.modus = "scenario"
            isochrones_scenario = await self.compute_isochrone(
                db, obj_in=obj_in_scenario, return_network=False
            )

            # Merge default and scenario isochrones
            result = GeoDataFrame(
                pd.concat([isochrones_default["isochrones"], isochrones_scenario["isochrones"]])
            )
        return result.reset_index(drop=True)

    async def calculate_reached_network(
        self, db: AsyncSession, *, obj_in: IsochroneSingle
    ) -> FeatureCollection:
        obj_in.speed = obj_in.speed / 3.6
        result = await self.compute_isochrone(db, obj_in=obj_in, return_network=True)
        result = result["network"]

        return result

    async def calculate_multi_isochrones(self, db: AsyncSession, *, obj_in) -> GeoDataFrame:

        obj_in.speed = obj_in.speed / 3.6
        await self.compute_multi_isochrone(db, obj_in=obj_in, return_network=False)

        if obj_in.modus == "default" or obj_in.modus == "scenario":
            result = await self.compute_multi_isochrone(db, obj_in=obj_in, return_network=False)
        elif obj_in.modus == "comparison":
            # Compute default isochrones
            obj_in_default = obj_in
            obj_in_default.modus = "default"
            isochrones_default = await self.compute_multi_isochrone(
                db, obj_in=obj_in, return_network=False
            )

            # Compute scenario isochrones
            obj_in_scenario = obj_in
            obj_in_scenario.modus = "scenario"
            isochrones_scenario = await self.compute_multi_isochrone(
                db, obj_in=obj_in, return_network=False
            )

            # Merge default and scenario isochrones
            result = GeoDataFrame(pd.concat([isochrones_default, isochrones_scenario]))
        return result.reset_index(drop=True)

    async def count_pois_multi_isochrones(self, db: AsyncSession, *, obj_in) -> dict:
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data["speed"] = obj_in_data["speed"] / 3.6
        sql = text(
            """SELECT count_pois
            FROM basic.count_pois_multi_isochrones(:user_id,:modus,:minutes,:speed,:region_type,:region,:amenities,:scenario_id,:active_upload_ids)"""
        )
        result = await db.execute(sql, obj_in_data)
        return result.fetchall()[0][0]

    async def calculate_pois_multi_isochrones(
        self, current_user, db: AsyncSession, *, obj_in
    ) -> GeoDataFrame:
        speed = obj_in.speed / 3.6
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data["speed"] = speed
        obj_in_data["user_id"] = current_user.id
        # Get starting points for multi-isochrone
        sql_starting_points = text(
            """SELECT x, y 
        FROM basic.starting_points_multi_isochrones(:user_id, :modus, :minutes, :speed, :amenities, :scenario_id, :active_upload_ids, :region_geom, :study_area_ids)"""
        )
        starting_points = await db.execute(sql_starting_points, obj_in_data)
        starting_points = starting_points.fetchall()
        obj_in_data["x"] = starting_points[0][0]
        obj_in_data["y"] = starting_points[0][1]

        obj_multi_isochrones = IsochroneMulti(
            user_id=obj_in.user_id,
            scenario_id=obj_in.scenario_id,
            speed=speed,
            modus=obj_in.modus,
            n=obj_in.n,
            minutes=obj_in.minutes,
            routing_profile=obj_in.routing_profile,
            active_upload_ids=obj_in.active_upload_ids,
            x=obj_in_data["x"],
            y=obj_in_data["y"],
        )

        # Compute Multi-Isochrones
        isochrones_result = await self.compute_multi_isochrone(
            db, obj_in=obj_multi_isochrones, return_network=False
        )
        isochrone_calculation_id = isochrones_result.isochrone_calculation_id.iloc[0]

        # Compute reached population
        if obj_in.region_type == "study_area":
            obj_population_multi_isochrones = {
                "isochrone_calculation_id": isochrone_calculation_id,
                "scenario_id": obj_in.scenario_id,
                "modus": obj_in.modus,
                "study_area_ids": obj_in.study_area_ids,
            }
            sql_reached_population = text(
                """SELECT * 
            FROM basic.reached_population_study_area(:isochrone_calculation_id, :scenario_id, :modus, :study_area_ids)
            """
            )
        else:
            obj_population_multi_isochrones = {
                "isochrone_calculation_id": isochrone_calculation_id,
                "scenario_id": obj_in.scenario_id,
                "modus": obj_in.modus,
                "region": obj_in.region[0],
            }
            sql_reached_population = text(
                """SELECT * 
            FROM basic.reached_population_polygon(:isochrone_calculation_id, :scenario_id, :modus, :region)
            """
            )

        result_reached_population = await db.execute(
            sql_reached_population, obj_population_multi_isochrones
        )
        await db.commit()

        dict_opportunities = {}
        [
            dict_opportunities.update({row[1]: row[2]})
            for row in result_reached_population.fetchall()
        ]
        isochrones_result["reached_opportunities"] = isochrones_result["step"].map(
            dict_opportunities
        )
        isochrones_result["routing_profile"] = obj_in.routing_profile
        isochrones_result["scenario_id"] = obj_in.scenario_id
        isochrones_result["modus"] = obj_in.modus

        return isochrones_result

    # ===================================
    async def __read_network(self, db, obj_in: IsochroneDTO) -> Any:
        isochrone_type = None
        if len(obj_in.starting_point.input) == 1:
            isochrone_type = IsochroneTypeEnum.single.value
        elif len(obj_in.starting_point.input) > 1:
            isochrone_type = IsochroneTypeEnum.multi.value
        else:
            raise Exception("Unknown calculation type")

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

        edges_network = read_sql(
            read_network_sql,
            legacy_engine,
            params={
                "x": obj_in.starting_point.input[0].lon,
                "y": obj_in.starting_point.input[0].lat,
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
        # obj_starting_point = models.IsochroneCalculation(
        #     calculation_type=isochrone_type,
        #     user_id=obj_in.user_id,
        #     scenario_id=None if obj_in.scenario.id == 0 else obj_in.scenario.id,
        #     starting_point=starting_point_geom,
        #     routing_profile=routing_profile,
        #     speed=obj_in.settings.speed,
        #     modus=obj_in.scenario.modus.value,
        #     parent_id=None,
        # )

        # db.add(obj_starting_point)
        # await db.commit()
        # await db.refresh(obj_starting_point)
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

    async def __amenity_intersect(self, grid_decoded, max_time) -> Any:
        """
        Calculate the intersection of the isochrone with the amenities (pois and population)
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
        test_geom_wkt = multipolygon_shape.wkt
        get_population_sum_query = f"""SELECT * FROM basic.get_population_sum(15, 'default'::text, ST_GeomFromText('{test_geom_wkt}', 4326), {grid_decoded["zoom"]})"""
        get_poi_one_entrance_sum_query = f"""SELECT * FROM basic.get_poi_one_entrance_sum(15, 'default'::text, ST_GeomFromText('{test_geom_wkt}', 4326), {grid_decoded["zoom"]})"""
        get_poi_more_entrance_sum_query = f"""SELECT * FROM basic.get_poi_more_entrance_sum(15, 'default'::text, ST_GeomFromText('{test_geom_wkt}', 4326), {grid_decoded["zoom"]})"""
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
        amenity_grid_count = amenity_r5_grid_intersect(
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

    async def calculate(self, db: AsyncSession, obj_in: IsochroneDTO) -> Any:
        """
        Calculate the isochrone for a given location and time"""
        result = None
        if obj_in.mode.value in [IsochroneMode.WALKING.value, IsochroneMode.CYCLING.value]:
            # === Fetch Network ===#
            network, starting_ids = await self.__read_network(db, obj_in)
            # === Compute Grid ===#
            grid = compute_isochrone(
                network, starting_ids, obj_in.settings.travel_time, obj_in.output.resolution
            )
            # === Amenity Intersect ===#
            # grid_decoded = await self.__amenity_intersect(grid, obj_in.settings.travel_time)
            grid_encoded = encode_r5_grid(grid)
            grid_decoded_test = decode_r5_grid(grid_encoded)
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
            grid_decoded = await self.__amenity_intersect(grid_decoded, 120)
            grid_encoded = encode_r5_grid(grid_decoded)
            result = Response(bytes(grid_encoded))
        return result


isochrone = CRUDIsochrone()
