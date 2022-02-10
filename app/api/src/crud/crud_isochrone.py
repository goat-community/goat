import io
import json
import os
import re
import shutil
import time
from datetime import datetime
from json import loads
from random import randint
from turtle import speed
from typing import Any

import pandas as pd
import sqlalchemy
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from geoalchemy2 import Geometry, WKTElement
from geojson import FeatureCollection
from geopandas import GeoDataFrame
from geopandas.io.sql import read_postgis
from pandas.io.sql import read_sql
from shapely.geometry import LineString, MultiPolygon, Point, Polygon
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import text

from src.db import models
from src.db.session import legacy_engine
from src.exts.cpp.bind import isochrone as isochrone_cpp
from src.schemas.isochrone import (
    IsochroneExport,
    IsochroneMulti,
    IsochroneMultiCountPois,
    IsochroneSingle,
)
from src.utils import sql_to_geojson


class CRUDIsochrone:
    async def compute_isochrone(
        self, db: AsyncSession, *, obj_in: IsochroneSingle, return_network=False
    ):
        obj_in_data = jsonable_encoder(obj_in)
        read_network_sql = text(
        """ 
        SELECT id, source, target, cost, reverse_cost, coordinates_3857 as geom, length_3857 AS length, starting_ids, starting_geoms
        FROM basic.fetch_network_routing(ARRAY[:x],ARRAY[:y], :max_cutoff, :speed, :modus, :scenario_id, :routing_profile)
        """
        )

        edges_network = read_sql(read_network_sql, legacy_engine, params=obj_in_data)
        starting_id = edges_network.iloc[0].starting_ids

        # There was an issue when removing the first row (which only contains the starting point) from the edges. So it was kept.
        edges_network = edges_network.drop(["starting_ids", "starting_geoms"], axis = 1)

        distance_limits = list(
            range(
                obj_in.max_cutoff // obj_in.n, obj_in.max_cutoff + 1, obj_in.max_cutoff // obj_in.n
            )
        )
        
        starting_point_geom = str(GeoDataFrame(
                {"geometry": Point(edges_network.iloc[-1:]["geom"].values[0][0])}, 
                crs="EPSG:3857", index=[0]).to_crs("EPSG:4326").to_wkt()["geometry"].iloc[0]
        )

        obj_starting_point = models.IsochroneCalculation(
            calculation_type="single_isochrone",
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
        
        obj_in_data["starting_point_id"] = obj_starting_point.id

        result = isochrone_cpp(edges_network, starting_id, distance_limits)
        isochrones = {"isochrone_calculation_id": [],"geometry": [], "step": []}

        for isochrone_result in result.isochrone:
            isochrones["isochrone_calculation_id"] = [
                obj_starting_point.id
            ] * isochrone_result.shape.__len__()
            for step, shape in isochrone_result.shape.items():
                isochrones["geometry"].append(MultiPolygon([Polygon(shape)]))
                isochrones["step"].append(step)
        isochrone_gdf = GeoDataFrame(isochrones, crs="EPSG:3857").to_crs("EPSG:4326")
        isochrone_gdf.rename_geometry("geom", inplace=True)
        isochrone_gdf.to_postgis(
            name="isochrone_feature", con=legacy_engine, schema="customer", if_exists="append"
        )

        # Compute reached opportunities
        sql = text(
            """SELECT * FROM basic.thematic_data_sum(:user_id,:starting_point_id,:modus,:scenario_id,:active_upload_ids) ORDER BY isochrone_feature_step"""
        )
        result_opportunities = await db.execute(sql, obj_in_data)
        await db.commit()

        arr_reached_opportunities = []
        for i in result_opportunities:
            arr_reached_opportunities.append(i[2])

        isochrone_gdf = isochrone_gdf.sort_values(by=["step"])
        isochrone_gdf.insert(3, "reached_opportunities", arr_reached_opportunities, True)
        isochrone_gdf.insert(4, "modus", obj_in.modus, True)
        return_obj = {"isochrones": isochrone_gdf}

        if return_network == True:
            features = []
            for edge in result.network:
                feature = {
                    "geometry": {"type": "LineString", "coordinates": edge.shape},
                    "type": "Feature",
                    "properties": {
                        "edge_id": edge.edge,
                        "isochrone_calculation_id": obj_starting_point.id,
                        "cost": max(edge.start_cost, edge.end_cost),
                        "start_cost": edge.start_cost,
                        "end_cost": edge.end_cost,
                        "start_perc": edge.start_perc,
                        "end_perc": edge.end_perc,
                    },
                }
                features.append(feature)

            network_feature_collection = {"type": "FeatureCollection", "features": features}

            return_obj["network"] = network_feature_collection

        return return_obj

    async def compute_multi_isochrone(
        self, db: AsyncSession, *, obj_in: IsochroneMulti, return_network=False
    ):
        obj_in_data = jsonable_encoder(obj_in)
        read_network_sql = text(
        """ 
        SELECT id, source, target, cost, reverse_cost, coordinates_3857 as geom, length_3857 AS length, starting_ids, starting_geoms
        FROM basic.fetch_network_routing(ARRAY[:x],ARRAY[:y], :max_cutoff, :speed, :modus, :scenario_id, :routing_profile)
        """
        )
        edges_network = read_sql(read_network_sql, legacy_engine, params=obj_in_data)

        starting_id = edges_network.iloc[0].starting_ids

        # There was an issue when removing the first row (which only contains the starting point) from the edges. So it was kept.
        edges_network = edges_network.drop(["starting_ids", "starting_geoms"], axis = 1)

        distance_limits = list(
            range(
                obj_in.max_cutoff // obj_in.n, obj_in.max_cutoff + 1, obj_in.max_cutoff // obj_in.n
            )
        )
        
        starting_point_geom = str(GeoDataFrame(
                {"geometry": Point(edges_network.iloc[-1:]["geom"].values[0][0])}, 
                crs="EPSG:3857", index=[0]).to_crs("EPSG:4326").to_wkt()["geometry"].iloc[0]
        )

        obj_starting_point = IsochroneCalculationDB(
            calculation_type="single_isochrone",
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
        
        obj_in_data["starting_point_id"] = obj_starting_point.id

        result = isochrone_cpp(edges_network, starting_id, distance_limits)
        isochrones = {"isochrone_calculation_id": [],"geometry": [], "step": []}

        for isochrone_result in result.isochrone:
            isochrones["isochrone_calculation_id"] = [obj_starting_point.id] * isochrone_result.shape.__len__()
            for step, shape in isochrone_result.shape.items():
                isochrones["geometry"].append(MultiPolygon([Polygon(shape)]))
                isochrones["step"].append(step)
        isochrone_gdf = GeoDataFrame(isochrones, crs="EPSG:3857").to_crs("EPSG:4326")
        isochrone_gdf.rename_geometry("geom", inplace=True)
        isochrone_gdf.to_postgis(name='isochrone_feature', con=legacy_engine, schema='customer', if_exists='append')

        # Compute reached opportunities
        sql = text(
            """SELECT * FROM basic.thematic_data_sum(:user_id,:starting_point_id,:modus,:scenario_id,:active_upload_ids) ORDER BY isochrone_feature_step"""
        )
        result_opportunities = await db.execute(sql, obj_in_data)
        await db.commit()
        
        arr_reached_opportunities = []
        for i in result_opportunities:
            arr_reached_opportunities.append(i[2])
            
        isochrone_gdf = isochrone_gdf.sort_values(by=['step'])
        isochrone_gdf.insert(3, "reached_opportunities", arr_reached_opportunities, True)
        isochrone_gdf.insert(4, "modus", obj_in.modus, True)
        return_obj = {"isochrones": isochrone_gdf}
        
        return return_obj


    async def calculate_single_isochrone(
        self, db: AsyncSession, *, obj_in: IsochroneSingle
    ) -> FeatureCollection:

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
            isochrones_scenario = await self.compute_isochrone(db, obj_in=obj_in_scenario, return_network=False)

            # Merge default and scenario isochrones
            result = GeoDataFrame(
                pd.concat([isochrones_default["isochrones"], isochrones_scenario["isochrones"]])
            )
        return result.to_json()

    async def calculate_reached_network(
        self, db: AsyncSession, *, obj_in: IsochroneSingle
    ) -> FeatureCollection:
        if obj_in.modus == "default" or obj_in.modus == "scenario":
            result = await self.compute_isochrone(db, obj_in=obj_in, return_network=True)
            result = json.dumps(result["network"])
        elif obj_in.modus == "comparison":
            #Compute default network
            obj_in_default = obj_in
            obj_in_default.modus = "default"
            isochrones_default = await self.compute_isochrone(db, obj_in=obj_in_default, return_network=True)

            #Compute scenario network
            obj_in_scenario = obj_in
            obj_in_scenario.modus = "scenario"
            isochrones_scenario = await self.compute_isochrone(db, obj_in=obj_in_scenario, return_network=True)

            result = [isochrones_default["network"], isochrones_scenario["network"]]
        return result

    async def calculate_multi_isochrones(
        self, db: AsyncSession, *, obj_in: IsochroneMulti
    ) -> FeatureCollection:
        obj_in_data = jsonable_encoder(obj_in)
        sql = text(
            """SELECT * FROM multi_isochrones_api(:user_id,:minutes,:speed,:n,:routing_profile,:alphashape_parameter,:modus,:region_type,:region,:amenities, :scenario_id, :active_upload_ids)"""
        )
        result = await db.execute(sql, obj_in_data)
        await db.commit()
        return sql_to_geojson(result)

    async def count_pois_multi_isochrones(
        self, db: AsyncSession, *, obj_in: IsochroneMultiCountPois
    ) -> FeatureCollection:
        obj_in_data = jsonable_encoder(obj_in)
        sql = text(
            """SELECT row_number() over() AS gid, count_pois, region_name, geom FROM basic.count_pois_multi_isochrones(:user_id,:modus,:minutes,:speed,:region_type,:region,:amenities,:scenario_id,:active_upload_ids)"""
        )
        result = await db.execute(sql, obj_in_data)
        return sql_to_geojson(result)

    async def export_isochrone(self, db: AsyncSession, *, obj_in: IsochroneExport) -> Any:
        obj_in_data = jsonable_encoder(obj_in)
        sql = text(
            """SELECT gid, objectid, step, modus, parent_id, population, sum_pois::text, geom FROM isochrones WHERE objectid = :objectid"""
        )

        gdf = read_postgis(sql, legacy_engine, geom_col="geom", params=obj_in_data)

        file_name = "isochrone_export"
        dir_path = "/tmp/exports/{}/".format(time.strftime("%Y%m%d-%H%M%S"))
        os.makedirs(dir_path)
        gdf.to_file(dir_path + file_name)
        shutil.make_archive(file_name, "zip", dir_path)
        with open(file_name + ".zip", "rb") as f:
            data = f.read()

        os.remove(file_name + ".zip")
        shutil.rmtree(dir_path[0 : len(dir_path) - 1])
        response = StreamingResponse(io.BytesIO(data), media_type="application/zip")
        response.headers["Content-Disposition"] = "attachment; filename={}.zip".format(file_name)
        return response


isochrone = CRUDIsochrone()


#     edge_obj = {

#     }
#     full_edge_objs.append(edge_obj)

#     if edge.start_perc not in [0.0, 1.0] or edge.end_perc not in [0.0, 1.0] or edge.edge in [999999999,999999998]:
#         edge_obj["partial_edge"] = True
#         edge_obj["geom"] = 'Linestring(%s)' % re.sub(',([^,]*,?)', r'\1', str(edge.shape)).replace('[', '').replace(']', '')
#         partial_edge_objs.append(edge_obj)


# await db.execute(IsochroneEdgeDB.__table__.insert(), full_edge_objs)
# await db.execute(IsochroneEdgeDB.__table__.insert(), partial_edge_objs)
# await db.commit()
