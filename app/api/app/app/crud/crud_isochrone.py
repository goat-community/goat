import io
import os
import shutil
import time
from time import time
from typing import Any

import geopandas
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from geojson import FeatureCollection
from geopandas.io.sql import read_postgis
from pandas.io.sql import read_sql
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import text

from app.db.session import legacy_engine
from app.exts.cpp.bind import isochrone
from app.schemas.isochrone import (
    IsochroneExport,
    IsochroneMulti,
    IsochroneMultiCountPois,
    IsochroneSingle,
)
from app.utils import sql_to_geojson


class CRUDIsochrone:
    async def calculate_single_isochrone(
        self, db: AsyncSession, *, obj_in: IsochroneSingle
    ) -> FeatureCollection:
        obj_in_data = jsonable_encoder(obj_in)
        read_network_sql = text(
            """ 
        SELECT id, source, target, cost, reverse_cost, ST_AsGeoJSON(ST_Transform(geom,3857))::json->'coordinates' as geom, st_length(st_transform(geom,3857)) as length FROM fetch_network_routing(ARRAY[:x],ARRAY[:y], 1200., 1.33, 1, 1, :routing_profile)
         """
        )
        start_time = time()
        print("Calculation started: ")
        ways_network = read_sql(read_network_sql, legacy_engine, params=obj_in_data)
        read_end_time = time()
        print("read_network_sql time: ", read_end_time - start_time)
        # isochrone_shape = calculate(ways_network, [999999999], [300, 600, 900])
        print("isochrone_shape time: ", time() - read_end_time)
        sql = text(
            """
            SELECT gid, objectid, coordinates, ST_ASTEXT(ST_MAKEPOINT(coordinates[1], coordinates[2])) AS starting_point,
            step, speed::integer, modus, parent_id, sum_pois, ST_AsGeoJSON(geom) as geom
            FROM isochrones_api(:user_id,:scenario_id,:minutes,:x,:y,:n,:speed,:concavity,:modus,:routing_profile,NULL,NULL,NULL)
         """
        )
        result = await db.execute(sql, obj_in_data)
        await db.commit()
        return sql_to_geojson(result, geometry_type="geojson")

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
