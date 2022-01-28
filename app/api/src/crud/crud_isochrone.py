import io
import os
import shutil
import time
import re
from json import loads
from random import randint
from time import time
from turtle import speed
from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from geoalchemy2 import Geometry, WKTElement
from geojson import FeatureCollection
from geopandas.io.sql import read_postgis
from pandas.io.sql import read_sql
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import text
from geopandas import GeoDataFrame
from shapely.geometry import Point, LineString, Polygon, MultiPolygon
from datetime import datetime
from src.db.models.customer.isochrone_calculation import IsochroneCalculation as IsochroneCalculationDB
from src.db.models.customer.isochrone_feature import IsochroneFeature as IsochroneFeatureDB
from src.db.models.customer.isochrone_edge import IsochroneEdge as IsochroneEdgeDB

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
        self, db: AsyncSession, *, obj_in: IsochroneSingle
    ) -> FeatureCollection:
        obj_in_data = jsonable_encoder(obj_in)
        read_network_sql = text(
        """ 
        SELECT id, source, target, cost, reverse_cost, coordinates_3857 as geom, length_3857 AS length
        FROM basic.fetch_network_routing(ARRAY[:x],ARRAY[:y], :max_cutoff, :speed, :modus, :scenario_id, :routing_profile)
        """
        )
        edges_network = read_sql(read_network_sql, legacy_engine, params=obj_in_data)
        distance_limits = list(
            range(
                obj_in.max_cutoff // obj_in.n, obj_in.max_cutoff + 1, obj_in.max_cutoff // obj_in.n
            )
        )
        
        starting_point_geom = str(GeoDataFrame(
                {"geometry": Point(edges_network.iloc[-1:]["geom"].values[0][0])}, 
                crs="EPSG:3857", index=[0]).to_crs("EPSG:4326").to_wkt()["geometry"]
        )

        obj_starting_point = IsochroneCalculationDB(
            calculation_type="single_isochrone",
            user_id=obj_in.user_id,
            scenario_id=obj_in.scenario_id,
            starting_point=starting_point_geom,
            routing_profile=obj_in.routing_profile,
            speed=obj_in.speed,
            modus=obj_in.modus,
            parent_id=None,
        )

        db.add(obj_starting_point)
        await db.commit()
        await db.refresh(obj_starting_point)
        
        result = isochrone_cpp(edges_network, [999999999], distance_limits)
        
        isochrones = {"isochrone_calculation_id": [],"geometry": [], "step": []}

        
        for isochrone_result in result.isochrone:
            isochrones["isochrone_calculation_id"] = [obj_starting_point.id] * isochrone_result.shape.__len__()
            for step, shape in isochrone_result.shape.items():
                isochrones["geometry"].append(MultiPolygon([Polygon(shape)]))
                isochrones["step"].append(step)
        isochrone_gdf = GeoDataFrame(isochrones, crs="EPSG:3857").to_crs("EPSG:4326")
        isochrone_gdf.rename_geometry("geom", inplace=True)
        isochrone_gdf.to_postgis(name='isochrone_feature', con=legacy_engine, schema='customer', if_exists='append')


        before = datetime.now()
        full_edge_objs = []
        partial_edge_objs = []
        for edge in result.network:
            edge_obj = {
                "edge_id": edge.edge,
                "isochrone_calculation_id": obj_starting_point.id,
                "cost": max(edge.start_cost,edge.end_cost),
                "start_cost": edge.start_cost,
                "end_cost": edge.end_cost,
                "start_perc": edge.start_perc,
                "end_perc": edge.end_perc,
            }
            full_edge_objs.append(edge_obj)

            if edge.start_perc not in [0.0, 1.0] or edge.end_perc not in [0.0, 1.0] or edge.edge in [999999999,999999998]:
                edge_obj["partial_edge"] = True
                edge_obj["geom"] = 'Linestring(%s)' % re.sub(',([^,]*,?)', r'\1', str(edge.shape)).replace('[', '').replace(']', '')
                partial_edge_objs.append(edge_obj)

        await db.execute(IsochroneEdgeDB.__table__.insert(), full_edge_objs)
        await db.execute(IsochroneEdgeDB.__table__.insert(), partial_edge_objs)
        await db.commit()
        print('Calculation took: %s' % (datetime.now() - before).total_seconds())
        x=0
        #for edge in result.network:
            


        #


        #isochrone_gdf["step"] = isochrone_gdf["step"] // 60  # convert to minutes

        #isochrone_gdf.rename_geometry("geom", inplace=True)
        #return isochrone_gdf


    async def calculate_single_isochrone(
        self, db: AsyncSession, *, obj_in: IsochroneSingle
    ) -> FeatureCollection:

        if obj_in.modus == "default" or obj_in.modus == "scenario":
            isochrone = await self.compute_isochrone(db, obj_in=obj_in)
        elif obj_in.modus == "comparison":
            #Compute default isochrones
            obj_in_default = obj_in.update(modus="default")
            isochrones_default = self.compute_isochrone(db, obj_in=obj_in_default)

            #Compute scenario isochrones
            obj_in_scenario = obj_in.update(modus="scenario")
            isochrones_scenario = self.compute_isochrone(db, obj_in=obj_in_scenario)

        isochrone_gdf.to_postgis(
            "isochrones",
            legacy_engine,
            if_exists="append",
            dtype={"geom": Geometry(geometry_type="POLYGON", spatial_index=True, srid=4326)},
        )

        # refetch the isochrone to get sum pois
        # sum_pois_sql = f"""
        # PERFORM thematic_data_sum({isochrone_calculation_id},{obj_in.scenario_id},{obj_in.modus});
        # SELECT step, population, sum_pois FROM isochrones WHERE objectid = {isochrone_calculation_id} AND userid = {obj_in.user_id};
        # """
        # result = await db.execute(sum_pois_sql)
        return loads(isochrone_gdf.to_json())

    async def calculate_multi_isochrones(
        self, db: AsyncSession, *, obj_in: IsochroneMulti
    ) -> FeatureCollection:
        obj_in_data = jsonable_encoder(obj_in)
        sql = text(
            """SELECT * FROM multi_isochrones_api(:user_id,:scenario_id,:minutes,:speed,:n,:routing_profile,:alphashape_parameter,:modus,:region_type,:region,:amenities)"""
        )
        result = await db.execute(sql, obj_in_data)
        await db.commit()
        return sql_to_geojson(result)

    async def count_pois_multi_isochrones(
        self, db: AsyncSession, *, obj_in: IsochroneMultiCountPois
    ) -> FeatureCollection:
        obj_in_data = jsonable_encoder(obj_in)
        sql = text(
            """SELECT row_number() over() AS gid, count_pois, region_name, geom FROM count_pois_multi_isochrones(:user_id,:scenario_id,:modus,:minutes,:speed,:region_type,:region,array[:amenities])"""
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
