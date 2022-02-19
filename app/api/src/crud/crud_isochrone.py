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
from geopandas import GeoDataFrame, GeoSeries
from geopandas.io.sql import read_postgis
from pandas.io.sql import read_sql
from shapely.geometry import LineString, MultiPolygon, Point, Polygon
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import text
from src.utils import sql_geojson
from src.db import models
from src.db.session import legacy_engine
from src.exts.cpp.bind import isochrone as isochrone_cpp
from src.schemas.isochrone import (
    IsochroneExport,
    IsochroneMulti,
    IsochroneMultiCountPois,
    IsochroneSingle,
    IsochroneTypeEnum,
    IsochronePoiMulti
)

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
            starting_point_geom = str(GeoDataFrame(
                    {"geometry": Point(edges_network.iloc[-1:]["geom"].values[0][0])}, 
                    crs="EPSG:3857", index=[0]).to_crs("EPSG:4326").to_wkt()["geometry"].iloc[0]
            )
        elif calculation_type == IsochroneTypeEnum.multi:
            starting_point_geom = str(edges_network["starting_geoms"].iloc[0])

        edges_network = edges_network.drop(["starting_ids", "starting_geoms"], axis = 1)

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

        return edges_network, starting_id, distance_limits, obj_starting_point

    def result_to_gdf(self, result, starting_id):
        isochrones = {}
        for isochrone_result in result.isochrone:
            for step, shape in isochrone_result.shape.items():
                if step not in isochrones.keys():
                    isochrones[step] = GeoSeries(Polygon(shape))
                else:
                    isochrones[step] = GeoSeries(isochrones[step].union(Polygon(shape)))
        
        isochrones_multipolygon = {}
        for step in isochrones.keys():
            if isochrones[step][0].geom_type == "Polygon":
                isochrones_multipolygon[step] = MultiPolygon([isochrones[step][0]])
            elif isochrones[step][0].geom_type == "MultiPolygon":
                isochrones_multipolygon[step] = MultiPolygon(isochrones[step][0])
            else:
                raise Exception("Not correct geom type")

        isochrone_gdf = GeoDataFrame(
            {
                "step": list(isochrones_multipolygon.keys()),
                "geometry": GeoSeries(isochrones_multipolygon.values()).set_crs("EPSG:3857"), 
                "isochrone_calculation_id": [starting_id] * len(isochrones)
            }
        ).to_crs("EPSG:4326")

        isochrone_gdf.rename_geometry("geom", inplace=True)
        isochrone_gdf.to_postgis(name='isochrone_feature', con=legacy_engine, schema='customer', if_exists='append')
        return isochrone_gdf


    async def compute_isochrone(
        self, db: AsyncSession, *, obj_in: IsochroneSingle, return_network=False
    ):
        obj_in_data = jsonable_encoder(obj_in)
        edges_network, starting_id, distance_limits, obj_starting_point = await self.read_network(db, IsochroneTypeEnum.single.value, obj_in, obj_in_data)
        
        obj_in_data["starting_point_id"] = obj_starting_point.id

        # Convert the isochrones result to a geodataframe and save isochrone_feature to postgis
        result = isochrone_cpp(edges_network, starting_id, distance_limits)
        isochrone_gdf = self.result_to_gdf(result, obj_starting_point.id)

        # Compute reached opportunities
        sql = text(
            """SELECT * FROM basic.thematic_data_sum(:user_id,:starting_point_id,:modus,:scenario_id,:active_upload_ids) ORDER BY isochrone_feature_step"""
        )
        result_opportunities = await db.execute(sql, obj_in_data)
        await db.commit()

        #Update isochrones with reached opportunities
        for i in result_opportunities:
            gdf_index = isochrone_gdf[isochrone_gdf['step'] == i[1]].index[0]
            isochrone_gdf.loc[gdf_index, 'reached_opportunities'] = str(i[2])

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
    ) -> GeoDataFrame:
        obj_in_data = jsonable_encoder(obj_in)
        edges_network, starting_id, distance_limits, obj_starting_point = await self.read_network(db, IsochroneTypeEnum.multi.value, obj_in, obj_in_data)
        obj_in_data["starting_point_id"] = starting_id

        result = isochrone_cpp(edges_network, starting_id, distance_limits)
        isochrone_gdf = self.result_to_gdf(result, obj_starting_point.id)

        return isochrone_gdf

    async def calculate_single_isochrone(
        self, db: AsyncSession, *, obj_in: IsochroneSingle
    ) -> GeoDataFrame:

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
        return result

    async def calculate_reached_network(
        self, db: AsyncSession, *, obj_in: IsochroneSingle
    ) -> FeatureCollection:
        if obj_in.modus == "default" or obj_in.modus == "scenario":
            result = await self.compute_isochrone(db, obj_in=obj_in, return_network=True)
            result = json.dumps(result["network"])
        elif obj_in.modus == "comparison":
            # Compute default network
            obj_in_default = obj_in
            obj_in_default.modus = "default"
            isochrones_default = await self.compute_isochrone(
                db, obj_in=obj_in_default, return_network=True
            )

            # Compute scenario network
            obj_in_scenario = obj_in
            obj_in_scenario.modus = "scenario"
            isochrones_scenario = await self.compute_isochrone(
                db, obj_in=obj_in_scenario, return_network=True
            )

            result = [isochrones_default["network"], isochrones_scenario["network"]]
        return result

    async def calculate_multi_isochrones(
        self, db: AsyncSession, *, obj_in: IsochroneMulti
    ) -> GeoDataFrame:

        await self.compute_multi_isochrone(db, obj_in=obj_in, return_network=False)
   
        if obj_in.modus == "default" or obj_in.modus == "scenario":
            result = await self.compute_multi_isochrone(db, obj_in=obj_in, return_network=False)
        elif obj_in.modus == "comparison":
            # Compute default isochrones
            obj_in_default = obj_in
            obj_in_default.modus = "default"
            isochrones_default = await self.compute_multi_isochrone(db, obj_in=obj_in, return_network=False)

            # Compute scenario isochrones
            obj_in_scenario = obj_in
            obj_in_scenario.modus = "scenario"
            isochrones_scenario = await self.compute_multi_isochrone(db, obj_in=obj_in, return_network=False)

            # Merge default and scenario isochrones
            result = GeoDataFrame(
                pd.concat([isochrones_default, isochrones_scenario])
            )
        return result

    async def count_pois_multi_isochrones(
        self, db: AsyncSession, *, obj_in: IsochroneMultiCountPois
    ) -> dict:
        obj_in_data = jsonable_encoder(obj_in)
        sql = text(
            sql_geojson % """SELECT row_number() over() AS id, count_pois, region_name, geom 
            FROM basic.count_pois_multi_isochrones(:user_id,:modus,:minutes,:speed,:region_type,:region,:amenities,:scenario_id,:active_upload_ids)"""
        )
        result = await db.execute(sql, obj_in_data)
        
        return result.fetchall()[0][0] 

    async def calculate_pois_multi_isochrones(
        self, db: AsyncSession, *, obj_in: IsochronePoiMulti
    ) -> GeoDataFrame:
        obj_in_data = jsonable_encoder(obj_in)

        # Get starting points for multi-isochrone
        sql_starting_points = text('''SELECT x, y 
        FROM basic.starting_points_multi_isochrones(:modus, :minutes, :speed, :amenities, :scenario_id, :active_upload_ids, :region_geom, :study_area_ids)'''
        )
        starting_points = await db.execute(sql_starting_points, obj_in_data)
        starting_points = starting_points.fetchall()
        obj_in_data["x"] = starting_points[0][0]
        obj_in_data["y"] = starting_points[0][1]

        obj_multi_isochrones = IsochroneMulti(
            user_id=obj_in.user_id,
            scenario_id=obj_in.scenario_id,
            speed=obj_in.speed,
            modus=obj_in.modus,
            n=obj_in.n,
            minutes=obj_in.minutes,
            routing_profile=obj_in.routing_profile,
            active_upload_ids=obj_in.active_upload_ids,
            x=obj_in_data["x"],
            y=obj_in_data["y"]
        )   
        
        #Compute Multi-Isochrones
        isochrones_result = await self.compute_multi_isochrone(db, obj_in=obj_multi_isochrones, return_network=False)
        isochrone_calculation_id = isochrones_result.isochrone_calculation_id.iloc[0]

        #Compute reached population
        if obj_in.region_type == "study_area":
            obj_population_multi_isochrones = {
                "isochrone_calculation_id": isochrone_calculation_id,
                "scenario_id": obj_in.scenario_id,
                "modus": obj_in.modus,
                "study_area_ids": obj_in.study_area_ids,
            }
            sql_reached_population = text("""SELECT * 
            FROM basic.reached_population_study_area(:isochrone_calculation_id, :scenario_id, :modus, :study_area_ids)
            """)
        else: 
            obj_population_multi_isochrones = {
                "isochrone_calculation_id": isochrone_calculation_id,
                "scenario_id": obj_in.scenario_id,
                "modus": obj_in.modus,
                "region": obj_in.region,
            }
            sql_reached_population = text("""SELECT * 
            FROM basic.reached_population_polygon(:isochrone_calculation_id, :scenario_id, :modus, :region)
            """)
        
        result_reached_population = await db.execute(sql_reached_population, obj_population_multi_isochrones)
        await db.commit()
        
        for i in result_reached_population.fetchall():
            isochrones_result.loc[isochrones_result.step == i[0], "reached_opportunities"] = str(i[1])

        return isochrones_result



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
