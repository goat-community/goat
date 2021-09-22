import io
import os
import shutil
import time
from typing import Any

import geopandas as gpd
import pandas as pd
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from geojson import FeatureCollection
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from app.schemas.isochrone import (
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

    async def export_isochrone(self, db: AsyncSession, *, obj_in: IsochroneSingle) -> Any:
        obj_in_data = jsonable_encoder(obj_in)
        sql = text(
            """SELECT gid, objectid, step, modus, parent_id, population, sum_pois::text, geom FROM isochrones WHERE objectid = :objectid"""
        )
        gdf = gpd.GeoDataFrame.from_postgis(
            sql, db.get_bind(), geom_col="geom", params=obj_in_data
        )
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
