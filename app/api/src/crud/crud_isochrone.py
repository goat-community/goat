import io
import json
import os
import shutil
import time
import uuid
from collections import defaultdict
from errno import ELOOP
from typing import Any

import numpy as np
import pandas as pd
import pyproj
import requests
from fastapi import Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from geopandas import GeoDataFrame, GeoSeries, clip, read_parquet, read_postgis
from pandas import concat
from pandas.io.sql import read_sql
from shapely import wkb, wkt
from shapely.geometry import Point, box, shape
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import text

from src import crud
from src.core.config import settings
from src.core.isochrone import compute_isochrone
from src.crud.base import CRUDBase
from src.db import models
from src.db.session import legacy_engine
from src.jsoline import generate_jsolines, jsolines
from src.resources.enums import IsochroneExportType
from src.schemas.isochrone import (
    IsochroneDTO,
    IsochroneMode,
    IsochroneMultiRegionType,
    IsochroneOutputType,
    IsochroneStartingPointCoord,
    IsochroneTypeEnum,
)
from src.utils import (
    create_h3_grid,
    decode_r5_grid,
    delete_dir,
    encode_r5_grid,
    merge_dicts,
    remove_keys,
    geometry_to_pixel,
    group_opportunities_multi_isochrone,
    group_opportunities_single_isochrone,
    is_inside_sm_parallel,
    web_mercator_to_wgs84,
    wgs84_to_web_mercator,
)

web_mercator_proj = pyproj.Proj("EPSG:3857")


class CRUDIsochroneCalculation(
    CRUDBase[models.IsochroneCalculation, models.IsochroneCalculation, models.IsochroneCalculation]
):
    pass


isochrone_calculation = CRUDIsochroneCalculation(models.IsochroneCalculation)


class OpportunityIntersect:
    def __init__(
        self,
        input_geometries: GeoDataFrame,
        group_by_column: str = "id",
        user_id: int = 0,
        user_active_upload_ids: list = [],
        scenario_id: int = 0,
        hexagon_size: int = 6,
    ):
        """Intersect opportunity data with geometries.

        Args:
            input_geometries (GeoDataFrame): Geometries to intersect with opportunity data.
            group_by (str): The input_geometries column to group by. Defaults to "id".
            user_id (int, optional): The user id. Defaults to 0.
            user_active_upload_ids (list, optional): The user active upload ids. Defaults to [].
            scenario_id (int, optional): The user scenario id. Defaults to 0.
            hexagon_size (int, optional): The hexagon size of parque tiles. Defaults to 6.
        """
        if group_by_column not in input_geometries.columns:
            raise ValueError(f"Column {group_by_column} not in input_geometries.")
        self.input_geometries = input_geometries
        self.user_id = user_id
        self.user_active_upload_ids = user_active_upload_ids
        self.scenario_id = scenario_id
        self.group_by_column = group_by_column
        geometry_bounds = input_geometries["geometry"].apply(
            lambda geom: box(*geom.bounds, ccw=True)
        )
        bbox = geometry_bounds.unary_union
        self.bbox_wkt = bbox.wkt
        self.h3_grid_gdf = create_h3_grid(bbox, hexagon_size)

    def count_poi(self):
        """
        Count the number of opportunities for each cutoff.

        :return: A dictionary with the cummulative number of opportunities for each cutoff.

        """
        # - Excluded features that are modified by the user.
        # Returns list of poi uid [1k3uirdsd, 2k3uirdsd, 3k3uirdsd] of features that are modified.
        excluded_pois = []
        if self.scenario_id != 0:
            excluded_pois = pd.read_sql(
                f"SELECT * FROM basic.modified_pois({self.scenario_id})",
                legacy_engine,
            ).iloc[0][0]

        # - Get the poi categories that user has uploaded.
        # Returns {'true': [restaurant, shop...], 'false': [bus_stop, train_station...]}
        poi_categories = pd.read_sql(
            f"SELECT * FROM basic.poi_categories({self.user_id})",
            legacy_engine,
        ).iloc[0][0]
        poi_one_entrance = poi_categories["false"]
        poi_multiple_entrances = poi_categories["true"]

        # - Read categories uploaded by the user.
        # Returns list of categories [restaurant, shop...] that user has uploaded.
        poi_categories_data_uploads = pd.read_sql(
            f"SELECT * FROM basic.poi_categories_data_uploads({self.user_id})",
            legacy_engine,
        ).iloc[0]["poi_categories_data_uploads"]
        # add the poi_categories that user has uploaded to the poi_one_entrance list if not already there
        poi_one_entrance = list(set(poi_one_entrance) | set(poi_categories_data_uploads))
        # TODO: We are considering that data uploaded by the user is always one entrance. This might change in the future.

        # - READ BASE DATA FROM PARQUET FILES
        poi_gdf = []
        for h3_index in self.h3_grid_gdf["h3_index"]:
            try:
                layer_gdf = read_parquet(
                    f"{settings.CACHE_PATH}/parquet-h3-tiles/{h3_index}/poi.parquet"
                )
                poi_gdf.append(layer_gdf)
            except Exception as e:
                print(e)

        if len(poi_gdf) > 0:
            poi_gdf = concat(poi_gdf, ignore_index=True)
        else:
            poi_gdf = GeoDataFrame(columns=["uid", "category", "geometry"], crs="EPSG:4326")

        if len(excluded_pois) > 0:
            poi_gdf = poi_gdf[~poi_gdf["uid"].isin(excluded_pois)]

        poi_one_entrance_gdf = poi_gdf[poi_gdf["category"].isin(poi_one_entrance)]
        poi_multiple_entrances_gdf = poi_gdf[poi_gdf["category"].isin(poi_multiple_entrances)]

        # - READ USER DATA FROM DATABASE
        # TODO: This is a temporary solution. We should read the data from the parquet files.
        poi_user_one_entrance_gdf = None
        poi_user_multiple_entrances_gdf = None
        if len(self.user_active_upload_ids) > 0:
            poi_user_one_entrance_gdf = read_postgis(
                f"""SELECT * FROM customer.poi_user p WHERE ST_Intersects('SRID=4326;{self.bbox_wkt}'::geometry, p.geom) 
                    AND p.category IN (SELECT UNNEST(ARRAY{poi_one_entrance}::text[])) 
                    AND p.uid NOT IN (SELECT UNNEST(ARRAY{excluded_pois}::text[])) 
                    AND p.data_upload_id IN (SELECT UNNEST(ARRAY{self.user_active_upload_ids}::integer[]))""",
                legacy_engine,
                crs="EPSG:4326",
            )
            poi_user_multiple_entrances_gdf = read_postgis(
                f"""SELECT * FROM customer.poi_user p WHERE ST_Intersects('SRID=4326;{self.bbox_wkt}'::geometry, p.geom) 
                AND p.category IN (SELECT UNNEST(ARRAY{poi_multiple_entrances}::text[])) 
                AND p.uid NOT IN (SELECT UNNEST(ARRAY{excluded_pois}::text[])) 
                AND p.data_upload_id IN (SELECT UNNEST(ARRAY{self.user_active_upload_ids}::integer[]))""",
                legacy_engine,
                crs="EPSG:4326",
            )

        # - READ MODIFIED DATA FROM DATABASE
        # TODO: This is a temporary solution. We should read the data from the parquet files.
        poi_modified_one_entrance_gdf = None
        poi_modified_multiple_entrances_gdf = None

        if self.scenario_id != 0:
            poi_modified_one_entrance_gdf = read_postgis(
                f"""SELECT * FROM customer.poi_modified p WHERE ST_Intersects('SRID=4326;{self.bbox_wkt}'::geometry, p.geom) 
                    AND p.category IN (SELECT UNNEST(ARRAY{poi_one_entrance}::text[])) 
                    AND p.uid NOT IN (SELECT UNNEST(ARRAY{excluded_pois}::text[])) 
                    AND p.scenario_id = {self.scenario_id}""",
                legacy_engine,
                crs="EPSG:4326",
            )
            poi_modified_multiple_entrances_gdf = read_postgis(
                f"""SELECT * FROM customer.poi_modified p WHERE ST_Intersects('SRID=4326;{self.bbox_wkt}'::geometry, p.geom) 
                AND p.category IN (SELECT UNNEST(ARRAY{poi_multiple_entrances}::text[])) 
                AND p.uid NOT IN (SELECT UNNEST(ARRAY{excluded_pois}::text[])) 
                AND p.scenario_id = {self.scenario_id}""",
                legacy_engine,
                crs="EPSG:4326",
            )

        # - JOIN BASE DATA WITH USER DATA AND MODIFIED DATA
        poi_count = defaultdict(dict)
        if any(
            item is not None
            for item in [
                poi_one_entrance_gdf,
                poi_user_one_entrance_gdf,
                poi_modified_one_entrance_gdf,
            ]
        ):
            poi_one_entrance_gdf = concat(
                [poi_one_entrance_gdf, poi_user_one_entrance_gdf, poi_modified_one_entrance_gdf],
                ignore_index=True,
            )
            # Poi with one entrance.
            poi_one_entrance_gdf_join = self.input_geometries.sjoin(
                poi_one_entrance_gdf, predicate="intersects", how="inner"
            )

            poi_one_entrance_gdf_grouped = poi_one_entrance_gdf_join.groupby(
                [self.group_by_column, "category"]
            )["uid"].count()
            # loop all poi_one_entrance_gdf_gruped
            for (group_by_column, category), value in poi_one_entrance_gdf_grouped.items():
                poi_count[group_by_column][category] = value

        # Poi with multiple entrances. Pois with same name and category are considered as one poi.
        # This is usually the case for bus stops, train stations, etc.
        if any(
            item is not None
            for item in [
                poi_multiple_entrances_gdf,
                poi_user_multiple_entrances_gdf,
                poi_modified_multiple_entrances_gdf,
            ]
        ):
            poi_multiple_entrances_gdf = concat(
                [
                    poi_multiple_entrances_gdf,
                    poi_user_multiple_entrances_gdf,
                    poi_modified_multiple_entrances_gdf,
                ],
                ignore_index=True,
            )

            poi_multiple_entrances_gdf_join = self.input_geometries.sjoin(
                poi_multiple_entrances_gdf, predicate="intersects", how="inner"
            )

            agg_func = {}
            if self.group_by_column == "minute":
                # relevant for isochrone inputs
                agg_func = {"minute": "mean"}
            else:
                # case when a multi entrance poi is in multiple shapes
                agg_func = {self.group_by_column: "_".join}

            poi_multiple_entrances_gdf_grouped = (
                poi_multiple_entrances_gdf_join.groupby(["category", "name"])
                .agg(agg_func)
                .reset_index()
            )
            if self.group_by_column == "minute":
                poi_multiple_entrances_gdf_grouped["minute"] = poi_multiple_entrances_gdf_grouped[
                    "minute"
                ].astype(int)

            poi_multiple_entrances_gdf_grouped = poi_multiple_entrances_gdf_grouped.groupby(
                [self.group_by_column, "category"]
            )["name"].count()

            # loop all poi_one_entrance_gdf_gruped
            for (group_by_column, category), value in poi_multiple_entrances_gdf_grouped.items():
                poi_count[group_by_column][category] = value

        return dict(poi_count)

    def count_population(self):
        """
        Count the number of population for each cutoff.

        :return: A dictionary with the cummulative number of population for each cutoff.

        """
        # - Excluded features that are modified by the user.
        # Returns list of populationv uid [1k3uirdsd, 2k3uirdsd, 3k3uirdsd] of features that are modified.
        excluded_buildings = []
        if self.scenario_id != 0:
            excluded_buildings = pd.read_sql(
                f"SELECT * FROM basic.modified_buildings({self.scenario_id})",
                legacy_engine,
            ).iloc[0][0]

        # - READ BASE DATA FROM PARQUET FILES
        population_gdf = []
        for h3_index in self.h3_grid_gdf["h3_index"]:
            try:
                layer_gdf = read_parquet(
                    f"{settings.CACHE_PATH}/parquet-h3-tiles/{h3_index}/population.parquet"
                )
                population_gdf.append(layer_gdf)
            except Exception as e:
                print(e)

        if len(population_gdf) > 0:
            population_gdf = concat(population_gdf, ignore_index=True)
        else:
            population_gdf = GeoDataFrame(
                columns=["population", "building_id", "geometry"], crs="EPSG:4326"
            )

        if len(excluded_buildings) > 0:
            population_gdf = population_gdf[
                ~population_gdf["building_id"].isin(excluded_buildings)
            ]

        # - READ MODIFIED DATA FROM DATABASE
        population_modified_gdf = None
        if self.scenario_id != 0:
            population_modified_gdf = read_postgis(
                f"""SELECT * FROM customer.population_modified p WHERE ST_Intersects('SRID=4326;{self.bbox_wkt}'::geometry, p.geom) 
                AND p.building_modified_id NOT IN (SELECT UNNEST(ARRAY{excluded_buildings}::integer[])) 
                AND p.scenario_id = {self.scenario_id}""",
                legacy_engine,
                crs="EPSG:4326",
            )

        # - JOIN BASE DATA WITH USER DATA AND MODIFIED DATA
        population_count = defaultdict(dict)
        if any(item is not None for item in [population_gdf, population_modified_gdf]):
            population_gdf = concat(
                [population_gdf, population_modified_gdf],
                ignore_index=True,
            )

            population_gdf_join = self.input_geometries.sjoin(
                population_gdf, predicate="intersects", how="inner"
            )
            population_gdf_grouped = population_gdf_join.groupby(self.group_by_column).agg(
                {"population": "sum"}
            )
            for (key, value) in population_gdf_grouped.iterrows():
                population_count[key]["population"] = value["population"]

        return dict(population_count)

    def count_aoi(self):
        """
        Count the total area of aois for each cutoff.

        :return: A dictionary with the cummulative area of aois for each cutoff.

        """

        # - READ BASE DATA FROM PARQUET FILES
        aoi_gdf = []
        for h3_index in self.h3_grid_gdf["h3_index"]:
            try:
                layer_gdf = read_parquet(
                    f"{settings.CACHE_PATH}/parquet-h3-tiles/{h3_index}/aoi.parquet"
                )
                aoi_gdf.append(layer_gdf)
            except Exception as e:
                print(e)

        if len(aoi_gdf) > 0:
            aoi_gdf = concat(aoi_gdf, ignore_index=True)
        else:
            aoi_gdf = GeoDataFrame(columns=["category", "geometry"], crs="EPSG:4326")

        aoi_count = defaultdict(dict)
        if any(item is not None for item in [aoi_gdf]):
            input_geometries_gdf_3857 = self.input_geometries.to_crs("EPSG:3857")
            aoi_gdf_3857 = aoi_gdf.to_crs("EPSG:3857")
            aoi_gdf_join = input_geometries_gdf_3857.overlay(aoi_gdf_3857, how="intersection")
            aoi_gdf_grouped = aoi_gdf_join.groupby([self.group_by_column, "category"]).apply(
                lambda x: x.area.sum()
            )

        for (group_by_column, category), value in aoi_gdf_grouped.items():
            aoi_count[group_by_column][category] = value

        return dict(aoi_count)


class CRUDIsochrone:
    def restructure_dict(self, original_dict, max_minute=None):
        """
        Restructures a dictionary of counts of various categories at different minutes
        into a dictionary of cumulative counts of categories at each minute.

        Args:
        - original_dict (dict): A dictionary of the form {minute: {category: count, ...}, ...},
        where minute is an integer, category is a string, and count is an integer.
        - max_minute (int): The maximum minute to consider. If None, the maximum minute is
        automatically determined from the original dictionary.

        Returns:
        - new_dict (dict): A dictionary of the form {category: [count1, count2, ...]},
        where count1, count2, ... are the cumulative counts of the category at each minute.

        Example usage:
        original_dict = {
            1: {"atm": 3, "post": 4},
            2: {"atm": 3, "post": 4, "park": 300}
        }
        new_dict = restructure_dict(original_dict)
        print(new_dict)
        # Output: {"atm": [3, 6], "post": [4, 8], "park": [0, 300]}

        In the returned dictionary, the root keys are the categories from the original dictionary,
        and each value is a list of the cumulative counts of the category at each minute.
        """
        # Find the maximum minute and collect all categories
        if max_minute is None:
            max_minute = max(original_dict.keys())
        categories = set()
        for minute_dict in original_dict.values():
            categories.update(minute_dict.keys())

        # Convert the original dictionary to a 2D NumPy array
        arr = np.zeros((len(categories), max_minute))

        for i, category in enumerate(categories):
            for j in range(max_minute):
                if j + 1 in original_dict:
                    arr[i, j] = original_dict[j + 1].get(category, 0)

        # Compute the cumulative sum along the rows
        cumulative_arr = arr.cumsum(axis=1)

        # Convert the result back to a dictionary
        new_dict = {category: [] for category in categories}
        for i, category in enumerate(categories):
            for j in range(max_minute):
                if j < cumulative_arr.shape[1]:
                    new_dict[category].append(cumulative_arr[i, j])
                else:
                    new_dict[category].append(new_dict[category][-1])

        # Step 5: Return the newly created dictionary
        return new_dict

    async def read_network(self, db, obj_in: IsochroneDTO, current_user, isochrone_type, table_prefix=None) -> Any:

        sql_text = ""
        if isochrone_type == IsochroneTypeEnum.single.value:
            sql_text = f"""SELECT id, source, target, cost, reverse_cost, coordinates_3857 as geom, length_3857 AS length, starting_ids, starting_geoms
            FROM basic.fetch_network_routing(ARRAY[:x],ARRAY[:y], :max_cutoff, :speed, :modus, :scenario_id, :routing_profile)
            """
        elif isochrone_type == IsochroneTypeEnum.multi.value:
            sql_text = f"""SELECT id, source, target, cost, reverse_cost, coordinates_3857 as geom, length_3857 AS length, starting_ids, starting_geoms
            FROM basic.fetch_network_routing_multi(:x,:y, :max_cutoff, :speed, :modus, :scenario_id, :routing_profile)
            """
        elif isochrone_type == IsochroneTypeEnum.heatmap.value:
            sql_text = f"""SELECT id, source, target, cost, reverse_cost, coordinates_3857 as geom, length_3857 AS length, starting_ids, starting_geoms
            FROM basic.fetch_network_routing_heatmap(:x,:y, :max_cutoff, :speed, :modus, :scenario_id, :routing_profile, :table_prefix)
            """

        read_network_sql = text(sql_text)
        routing_profile = None
        if obj_in.mode.value == IsochroneMode.WALKING.value:
            routing_profile = obj_in.mode.value + "_" + obj_in.settings.walking_profile.value

        if obj_in.mode.value == IsochroneMode.CYCLING.value:
            routing_profile = obj_in.mode.value + "_" + obj_in.settings.cycling_profile.value

        x = y = None
        if (
            isochrone_type == IsochroneTypeEnum.multi.value
            or isochrone_type == IsochroneTypeEnum.heatmap.value
        ):
            if isinstance(obj_in.starting_point.input[0], IsochroneStartingPointCoord):
                x = [point.lon for point in obj_in.starting_point.input]
                y = [point.lat for point in obj_in.starting_point.input]
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
                "table_prefix": table_prefix,
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

        if (
            isochrone_type == IsochroneTypeEnum.single.value
            or isochrone_type == IsochroneTypeEnum.multi.value
        ):
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
        network = None
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
            network = network.iloc[1:, :]
            grid, network = compute_isochrone(
                network, starting_ids, obj_in.settings.travel_time, obj_in.output.resolution
            )
        # == Public transport isochrone ==
        else:
            # TODO: get the mapping dynamically from the database based on the study area
            weekday = obj_in.settings.weekday
            available_dates = {
                0: "2022-05-16",
                1: "2022-05-17",
                2: "2022-05-18",
                3: "2022-05-19",
                4: "2022-05-20",
                5: "2022-05-21",
                6: "2022-05-22",
            }

            payload = {
                "accessModes": obj_in.settings.access_mode.value.upper(),
                "transitModes": ",".join(x.value.upper() for x in obj_in.settings.transit_modes),
                "bikeSpeed": obj_in.settings.bike_speed,
                "walkSpeed": obj_in.settings.walk_speed,
                "bikeTrafficStress": obj_in.settings.bike_traffic_stress,
                "date": available_dates[weekday],
                "fromTime": obj_in.settings.from_time,
                "toTime": obj_in.settings.to_time,
                "maxTripDurationMinutes": 120,  # TODO: Fix this
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
            # TODO: Get the project id.
            payload["projectId"] = "630c0014aad8682ef8461b44"
            study_area = await crud.user.get_active_study_area(db, current_user)
            study_area_bounds = study_area["bounds"]
            payload["bounds"] = {
                "north": study_area_bounds[3],
                "south": study_area_bounds[1],
                "west": study_area_bounds[0],
                "east": study_area_bounds[2],
            }
            headers = {}
            if settings.R5_AUTHORIZATION:
                headers["Authorization"] = settings.R5_AUTHORIZATION
            response = requests.post(
                settings.R5_API_URL + "/analysis", json=payload, headers=headers
            )
            grid = decode_r5_grid(response.content)

        isochrone_shapes = generate_jsolines(
            grid=grid, travel_time=obj_in.settings.travel_time, percentile=5
        )
        if obj_in.output.type.value != IsochroneOutputType.NETWORK.value:
            # Opportunity intersect
            opportunity_user_args = {
                "user_id": current_user.id,
                "user_active_upload_ids": current_user.active_data_upload_ids,
                "scenario_id": obj_in.scenario.id,
            }
            if isochrone_type == IsochroneTypeEnum.single.value:
                start = time.time()
                opportunity_intersect = OpportunityIntersect(
                    input_geometries=isochrone_shapes["incremental"],
                    group_by_column="minute",
                    **opportunity_user_args,
                )

                poi_count = opportunity_intersect.count_poi()
                population_count = opportunity_intersect.count_population()
                opportunity_count = [poi_count, population_count]
                if obj_in.mode.value != IsochroneMode.TRANSIT.value:
                    aoi_count = opportunity_intersect.count_aoi()
                    opportunity_count.append(aoi_count)

                opportunity_count = merge_dicts(*opportunity_count)
                opportunity_count = self.restructure_dict(opportunity_count)
                grid["accessibility"] = opportunity_count
                print(f"Opportunity intersect took {time.time() - start} seconds")
            elif isochrone_type == IsochroneTypeEnum.multi.value:
                if obj_in.starting_point.region_type == IsochroneMultiRegionType.STUDY_AREA:
                    regions = read_postgis(
                        f"SELECT * FROM basic.sub_study_area WHERE id = ANY(ARRAY[{list(map(int, obj_in.starting_point.region))}])",
                        legacy_engine,
                    )
                else:
                    # if there is only one region, name is polygon, otherwise it is the index + 1
                    if len(obj_in.starting_point.region) == 1:
                        name = "polygon"
                    else:
                        name = np.arange(1, len(obj_in.starting_point.region) + 1)
                    # name is the list index + 1 as currently there is no name for the user drawn regions
                    regions = GeoDataFrame(
                        {
                            "name": name,
                            "geom": (GeoSeries.from_wkt(obj_in.starting_point.region)),
                        }
                    )
                    regions.set_geometry("geom", inplace=True)
                    regions.set_crs(epsg=4326, inplace=True)
                if "geometry" not in regions.columns:
                    regions.rename_geometry("geometry", inplace=True)
                intersected_regions = []
                for idx, region in regions.iterrows():
                    # clip the isochrone shapes to the regions
                    isochrone_clip = clip(isochrone_shapes["incremental"], region["geometry"])
                    # adds a column which combines the region id and the isochrone minute to avoid calling the opportunity intersect multiple times within the loop
                    isochrone_clip["region"] = isochrone_clip.apply(
                        lambda x: "{}_x_{}".format(region["name"], x.minute), axis=1
                    )
                    isochrone_clip.set_crs(epsg=4326, inplace=True)

                    intersected_regions.append(isochrone_clip)

                # intersect the original region shapes if the user has selected to draw the regions
                # study areas already have the population count from DB so no need to intersect
                if obj_in.starting_point.region_type == IsochroneMultiRegionType.DRAW:
                    regions["region"] = regions.apply(
                        lambda x: "{}_x_{}".format(x["name"], "total"), axis=1
                    )
                    intersected_regions.append(regions)

                intersected_regions = pd.concat(intersected_regions, ignore_index=True)
                # intersect the clipped isochrone shapes with the opportunity data
                opportunity_intersect = OpportunityIntersect(
                    input_geometries=intersected_regions,
                    group_by_column="region",
                    **opportunity_user_args,
                )
                population_count = opportunity_intersect.count_population()
                # split the dictionary based on region groups
                regions_count = {}
                for key, count_value in population_count.items():
                    region, count_key = key.split("_x_")
                    if count_key != "total":
                        count_key = int(count_key)
                    if region not in regions_count:
                        regions_count[region] = {}
                    regions_count[region][count_key] = count_value

                opportunity_count = defaultdict(dict)
                # population count
                for region, population_count in regions_count.items():
                    population_reached = self.restructure_dict(
                        remove_keys(population_count, ["total"]),
                        max_minute=obj_in.settings.travel_time,
                    )
                    if population_count.get("total") and population_count.get("total").get(
                        "population"
                    ):
                        total_population = int(population_count.get("total")["population"])
                    else:
                        total_population = regions.query(f'name == "{region}"').iloc[0][
                            "population"
                        ]

                    opportunity_count[region]["total_population"] = int(total_population)
                    opportunity_count[region]["reached_population"] = population_reached[
                        "population"
                    ]

                grid["accessibility"] = dict(opportunity_count)
            grid_encoded = encode_r5_grid(grid)
            result = Response(bytes(grid_encoded))
        else:
            result = network
        return result


isochrone = CRUDIsochrone()
