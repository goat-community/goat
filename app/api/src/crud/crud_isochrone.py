from functools import cache
import io
import json
import os
import shutil
import time
import uuid
from collections import defaultdict
from typing import Any

import numpy as np
import pandas as pd
import geopandas as gpd
import requests
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from geopandas import GeoDataFrame, GeoSeries, clip, read_postgis
from pandas.io.sql import read_sql
from shapely.geometry import Point, shape
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import text
import geopandas as gpd
from shapely.geometry import Polygon
from pyproj import Transformer

from src.core.config import settings
from src.core.isochrone import compute_isochrone
from src.core.opportunity import OpportunityIsochroneCount
from src.db import models
from src.db.session import legacy_engine
from src.jsoline import generate_jsolines
from src.resources.enums import IsochroneExportType
from src.schemas.isochrone import (
    IsochroneDTO,
    IsochroneMode,
    IsochroneMultiRegionType,
    IsochroneStartingPointCoord,
    IsochroneTypeEnum,
    R5AvailableDates,
    R5ProjectIDCarOnly,
    R5TravelTimePayloadTemplate,
)
from src.utils import (
    buffer,
    decode_r5_grid,
    delete_dir,
    encode_r5_grid,
    merge_dicts,
    remove_keys,
)


class CRUDIsochrone:
    def restructure_dict(self, original_dict, max_value=None, step=1):
        """
        Restructures a dictionary of counts of various categories at different steps
        into a dictionary of cumulative counts of categories at each step.

        Args:
        - original_dict (dict): A dictionary of the form {minute: {category: count, ...}, ...},
        where minute is an integer, category is a string, and count is an integer.
        - max_value (int): The maximum step (e.g minute) to consider. If None, the maximum value is
        automatically determined from the original dictionary.
        - step (int): The step size. For example, if step=1, the cumulative counts are computed

        Returns:
        - new_dict (dict): A dictionary of the form {category: [count1, count2, ...]},
        where count1, count2, ... are the cumulative counts of the category at each step.

        Example usage:
        original_dict = {
            1: {"atm": 3, "post": 4},
            2: {"atm": 3, "post": 4, "park": 300}
        }
        new_dict = restructure_dict(original_dict)
        print(new_dict)
        # Output: {"atm": [3, 6], "post": [4, 8], "park": [0, 300]}

        In the returned dictionary, the root keys are the categories from the original dictionary,
        and each value is a list of the cumulative counts of the category at each step.
        """
        # Find the maximum step and collect all categories
        if len(original_dict) == 0:
            return {}
        if max_value is None:
            max_value = max(original_dict.keys())
        categories = set()
        for steps_dict in original_dict.values():
            categories.update(steps_dict.keys())

        # Convert the original dictionary to a 2D NumPy array
        arr = np.zeros((len(categories), max_value // step))

        for i, category in enumerate(categories):
            for index, j in enumerate(range(0, max_value, step)):
                if j + step in original_dict:
                    arr[i, index] = original_dict[j + step].get(category, 0)

        # Compute the cumulative sum along the rows
        cumulative_arr = arr.cumsum(axis=1)

        # Convert the result back to a dictionary
        new_dict = {category: [] for category in categories}
        for i, category in enumerate(categories):
            for j in range(max_value):
                if j < cumulative_arr.shape[1]:
                    new_dict[category].append(cumulative_arr[i, j])
                else:
                    new_dict[category].append(new_dict[category][-1])

        # Step 5: Return the newly created dictionary
        return new_dict

    def read_network(
        self, db, obj_in: IsochroneDTO, current_user, isochrone_type, table_prefix=None
    ) -> Any:
        sql_text = ""
        if isochrone_type == IsochroneTypeEnum.single.value:
            sql_text = """SELECT id, source, target, cost, reverse_cost, coordinates_3857 as geom, length_3857 AS length, starting_ids, starting_geoms
            FROM basic.fetch_network_routing(ARRAY[:x],ARRAY[:y], :max_cutoff, :speed, :modus, :scenario_id, :routing_profile)
            """
        elif isochrone_type == IsochroneTypeEnum.multi.value:
            sql_text = """SELECT id, source, target, cost, reverse_cost, coordinates_3857 as geom, length_3857 AS length, starting_ids, starting_geoms
            FROM basic.fetch_network_routing_multi(:x,:y, :max_cutoff, :speed, :modus, :scenario_id, :routing_profile)
            """
        elif isochrone_type == IsochroneTypeEnum.heatmap.value:
            sql_text = """
            SELECT id, source, target, cost, reverse_cost, coordinates_3857 as geom, length_3857 AS length, starting_ids, starting_geoms
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
                starting_points = self.starting_points_opportunities(current_user, db, obj_in)
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
                "speed": obj_in.settings.speed / 3.6,
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
                speed=obj_in.settings.speed,
                modus=obj_in.scenario.modus.value,
                parent_id=None,
            )

            db.add(obj_starting_point)
            db.commit()

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
        return edges_network, starting_ids, starting_point_geom

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

    def starting_points_opportunities(
        self, current_user, db: AsyncSession, obj_in: IsochroneDTO
    ) -> Any:
        obj_in_data = {
            "user_id": current_user.id,
            "modus": obj_in.scenario.modus.value,
            "minutes": obj_in.settings.travel_time,
            "speed": obj_in.settings.speed / 3.6,
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
        starting_points = db.execute(sql_starting_points, obj_in_data)
        starting_points = starting_points.fetchall()
        return starting_points

    def calculate(
        self, db: AsyncSession, obj_in: IsochroneDTO, current_user: models.User, study_area_bounds
    ) -> Any:
        """
        Calculate the isochrone for a given location and time
        """
        grid = None
        result = None
        network = None
        step_size = 1
        max_value = 0
        if obj_in.settings.travel_time is not None:
            max_value = obj_in.settings.travel_time

        if len(obj_in.starting_point.input) == 1 and isinstance(
            obj_in.starting_point.input[0], IsochroneStartingPointCoord
        ):
            isochrone_type = IsochroneTypeEnum.single.value
        else:
            isochrone_type = IsochroneTypeEnum.multi.value

        # == Walking and cycling isochrone ==
        if obj_in.mode.value in [IsochroneMode.WALKING.value, IsochroneMode.CYCLING.value]:
            network, starting_ids, starting_point_geom = self.read_network(
                db, obj_in, current_user, isochrone_type
            )
            network = network.iloc[1:, :]
            grid, network = compute_isochrone(
                network,
                starting_ids,
                obj_in.settings.travel_time,
                obj_in.settings.speed / 3.6,
                obj_in.output.resolution,
            )
        # == Public transport isochrone ==
        elif obj_in.mode.value in [IsochroneMode.TRANSIT.value, IsochroneMode.CAR.value]:
            starting_point_geom = Point(
                obj_in.starting_point.input[0].lon, obj_in.starting_point.input[0].lat
            ).wkt

            weekday = obj_in.settings.weekday
            payload = R5TravelTimePayloadTemplate.copy()

            if obj_in.mode.value == IsochroneMode.CAR.value:
                payload["transitModes"] = ""
                payload["accessModes"] = "CAR"
                payload["projectId"] = R5ProjectIDCarOnly
            else:
                payload["transitModes"] = ",".join(
                    x.value.upper() for x in obj_in.settings.transit_modes
                )
                payload["accessModes"] = "WALK"
            payload["date"] = R5AvailableDates[weekday]
            payload["fromTime"] = obj_in.settings.from_time
            payload["toTime"] = obj_in.settings.to_time
            payload["directModes"] = obj_in.settings.access_mode.value.upper()
            payload["egressModes"] = obj_in.settings.egress_mode.value.upper()
            payload["fromLat"] = obj_in.starting_point.input[0].lat
            payload["fromLon"] = obj_in.starting_point.input[0].lon


            # Buffer the extend of the study area by 30km to ensure that the isochrone covers the entire study area
            poly = Polygon([(study_area_bounds[0], study_area_bounds[1]), (study_area_bounds[0], study_area_bounds[3]), (study_area_bounds[2], study_area_bounds[3]), (study_area_bounds[2], study_area_bounds[1])])
                        # Create a GeoDataFrame from the Polygon
            gdf = gpd.GeoDataFrame({'geometry': [poly]}, crs="EPSG:4326")

            # Transform to Web Mercator
            gdf = gdf.to_crs("EPSG:3857")

            # Buffer by 30km
            gdf['geometry'] = gdf.geometry.buffer(30000)

            # Transform back to WGS84
            gdf = gdf.to_crs("EPSG:4326")

            # Get the extent of the resulting buffered geometry
            study_area_bounds = tuple(list(gdf.total_bounds))

            # You can now use g (which is a GeoSeries containing the buffered polygon)
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

        if obj_in.mode.value in [IsochroneMode.BUFFER.value]:
            if isochrone_type == IsochroneTypeEnum.multi.value:
                starting_points = self.starting_points_opportunities(current_user, db, obj_in)
                x = starting_points[0][0]
                y = starting_points[0][1]
                starting_points_gdf = gpd.GeoDataFrame(
                    geometry=gpd.points_from_xy(x, y), crs="EPSG:4326"
                )
                starting_point_geom = str(starting_points_gdf["geometry"].to_wkt().to_list())
                max_value = obj_in.settings.buffer_distance // 50
            else:
                starting_point_geom = Point(
                    obj_in.starting_point.input[0].lon, obj_in.starting_point.input[0].lat
                ).wkt
                starting_points = [
                    Point(data.lon, data.lat) for data in obj_in.starting_point.input
                ]
                starting_points_gdf = gpd.GeoDataFrame(geometry=starting_points, crs="EPSG:4326")
            isochrone_shapes = buffer(
                starting_points_gdf=starting_points_gdf,
                buffer_distance=obj_in.settings.buffer_distance,
                increment=50,
            )
            group_by_column = "steps"
            grid = {
                "surface": [],
                "data": [],
                "width": 0,
                "height": 0,
                "west": 0,
                "north": 0,
                "zoom": 0,
                "depth": 1,
                "version": 0,
            }
        else:
            isochrone_shapes = generate_jsolines(
                grid=grid, travel_time=obj_in.settings.travel_time, percentile=5
            )
            group_by_column = "minute"
        # Opportunity intersect
        opportunity_user_args = {
            "user_id": current_user.id,
            "user_active_upload_ids": current_user.active_data_upload_ids,
            "scenario_id": obj_in.scenario.id,
        }
        if isochrone_type == IsochroneTypeEnum.single.value:
            start = time.time()
            opportunity_count = OpportunityIsochroneCount(
                input_geometries=isochrone_shapes["incremental"],
                **opportunity_user_args,
            )

            # Poi
            poi_count = opportunity_count.count_poi(group_by_column=group_by_column)
            # Population
            population_count = opportunity_count.count_population(
                group_by_columns=[group_by_column]
            )

            opportunities = [poi_count, population_count]
            if obj_in.mode.value != IsochroneMode.TRANSIT.value:
                # Aoi
                aoi_count = opportunity_count.count_aoi(
                    group_by_columns=[group_by_column, "category"]
                )
                opportunities.append(aoi_count)

            opportunities = merge_dicts(*opportunities)
            opportunities = self.restructure_dict(opportunities, step=step_size)
            grid["accessibility"] = {
                "starting_points": starting_point_geom,
                "opportunities": opportunities,
            }
            print(f"Opportunity intersect took {time.time() - start} seconds")
        elif isochrone_type == IsochroneTypeEnum.multi.value:
            if obj_in.starting_point.region_type == IsochroneMultiRegionType.STUDY_AREA:
                regions = read_postgis(
                    f"SELECT name, geom FROM basic.sub_study_area WHERE id = ANY(ARRAY[{list(map(int, obj_in.starting_point.region))}])",
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
            for _idx, region in regions.iterrows():
                # clip the isochrone shapes to the regions
                isochrone_clip = clip(isochrone_shapes["incremental"], region["geometry"])
                # adds a column which combines the region id and the isochrone minute to avoid calling the opportunity intersect multiple times within the loop

                isochrone_clip["region"] = isochrone_clip.apply(
                    lambda x: "{}_x_{}".format(region["name"], x.get(group_by_column)), axis=1
                )
                isochrone_clip.set_crs(epsg=4326, inplace=True)

                intersected_regions.append(isochrone_clip)

            # intersect the original region shapes as well
            regions["region"] = regions.apply(
                lambda x: "{}_x_{}".format(x["name"], "total"), axis=1
            )
            intersected_regions.append(regions)

            intersected_regions = pd.concat(intersected_regions, ignore_index=True)
            # intersect the clipped isochrone shapes with the opportunity data
            opportunity_count = OpportunityIsochroneCount(
                input_geometries=intersected_regions,
                **opportunity_user_args,
            )
            population_count = opportunity_count.count_population(group_by_columns=["region"])
            # split the dictionary based on region groups
            regions_count = {}
            for key, count_value in population_count.items():
                region, count_key = key.split("_x_")
                if count_key != "total":
                    count_key = int(count_key)
                if region not in regions_count:
                    regions_count[region] = {}
                regions_count[region][count_key] = count_value

            opportunities = defaultdict(dict)
            # population count
            for region, population_count in regions_count.items():
                population_reached = self.restructure_dict(
                    remove_keys(population_count, ["total"]), max_value=max_value
                )
                # Check if population_reached is empty
                if population_reached:
                    population_reached["population"] = [
                        int(x) for x in population_reached["population"]
                    ]
                else:
                    population_reached["population"] = [0] * (max_value // step_size)

                if population_count.get("total") and population_count.get("total").get(
                    "population"
                ):
                    total_population = int(population_count.get("total")["population"])
                else:
                    total_population = regions.query(f'name == "{region}"').iloc[0]["population"]

                opportunities[region]["total_population"] = int(total_population)
                opportunities[region]["reached_population"] = population_reached["population"]

            grid["accessibility"] = {
                "starting_points": starting_point_geom,
                "opportunities": dict(opportunities),
            }
        if obj_in.mode.value == IsochroneMode.BUFFER.value:
            grid["accessibility"]["buffer"] = {
                "steps": 50,  # in meters
                "distance": obj_in.settings.buffer_distance,
                "geojson": isochrone_shapes["full"].to_json(),
            }
        grid_encoded = encode_r5_grid(grid)
        if isochrone_type == IsochroneTypeEnum.single.value:
            geojson_result = self.build_geojson_single(isochrone_shapes, opportunities)
        elif isochrone_type == IsochroneTypeEnum.multi.value:
            geojson_result = self.build_geojson_multi(isochrone_shapes, opportunities)

        result = {
            "grid": grid_encoded,
            "geojson": geojson_result,
            "network": network,
        }
        return result

    def build_geojson_single(self, isochrone_shapes, opportunities):
        geojson = json.loads(isochrone_shapes["full"].to_json())
        for key, opportunity in opportunities.items():
            for cnt, value in enumerate(opportunity):
                geojson["features"][cnt]["properties"][key] = value
        return geojson

    def build_geojson_multi(self, isochrone_shapes, opportunities):
        @cache
        def sub_study_area_to_feature_name(sub_study_area, feature):
            return f"{feature}_{sub_study_area}"

        geojson = json.loads(isochrone_shapes["full"].to_json())
        population_keys = list(opportunities.keys())

        for cnt in range(len(geojson["features"])):
            for key in population_keys:
                feature_name = sub_study_area_to_feature_name(key, "total_population")
                sub_study_area_total_population = opportunities[key]["total_population"]
                geojson["features"][cnt]["properties"][
                    feature_name
                ] = sub_study_area_total_population

            for key in population_keys:
                feature_name = sub_study_area_to_feature_name(key, "reached_population")
                sub_study_area_population_count = opportunities[key]["reached_population"][cnt]
                geojson["features"][cnt]["properties"][
                    feature_name
                ] = sub_study_area_population_count

        return geojson


isochrone = CRUDIsochrone()
