import io
import os
import shutil
import time
from json import loads
from random import randint
from time import time
from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from geoalchemy2 import Geometry, WKTElement
from geojson import FeatureCollection
from geopandas.io.sql import read_postgis
from pandas.io.sql import read_sql
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import text

from app.db.session import legacy_engine
from app.exts.cpp.bind import isochrone as isochrone_cpp
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
        SELECT id, source, target, cost, reverse_cost, ST_AsGeoJSON(ST_Transform(geom,3857))::json->'coordinates' as geom, st_length(st_transform(geom,3857)) as length 
        FROM fetch_network_routing(ARRAY[:x],ARRAY[:y], :max_cutoff, :speed, :modus, :scenario_id, :routing_profile)
         """
        )
        ways_network = read_sql(read_network_sql, legacy_engine, params=obj_in_data)
        distance_limits = list(
            range(
                obj_in.max_cutoff // obj_in.n, obj_in.max_cutoff + 1, obj_in.max_cutoff // obj_in.n
            )
        )
        isochrone_calculation_id = randint(
            1, 2147483647
        )  # 2147483647 is the max value for integer in postgres
        isochrone_gdf = isochrone_cpp(ways_network, [999999999], distance_limits)
        isochrone_gdf["userid"] = obj_in.user_id
        isochrone_gdf["scenario_id"] = obj_in.scenario_id
        isochrone_gdf["speed"] = obj_in.speed * 3.6  # convert back to km/h
        isochrone_gdf[
            "starting_point"
        ] = f"POINT({obj_in.x} {obj_in.y})"  # only for single-isochorne for multi-isochrone starting points are amenity points
        isochrone_gdf["step"] = isochrone_gdf["step"] // 60  # convert to minutes
        isochrone_gdf["modus"] = obj_in.modus
        isochrone_gdf["concavity"] = obj_in.concavity
        isochrone_gdf["objectid"] = isochrone_calculation_id
        isochrone_gdf.rename_geometry("geom", inplace=True)
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
