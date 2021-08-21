from app.utils import without_keys
from app.schemas.isochrone import (
    IsochroneMulti,
    IsochroneMultiCountPois,
    IsochroneSingle,
)
from typing import Any, List
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from fastapi.encoders import jsonable_encoder
from geojson import Feature, FeatureCollection, loads as geojsonloads
from shapely.wkb import loads as wkbloads


class CRUDIsochrone:
    def sql_to_geojson(
        self,
        sql_result: Any,
        geometry_name: str = "geom",
        geometry_type: str = "wkb",  # wkb | geojson (wkb is postgis geometry which is stored as hex)
        exclude_properties: List = [],
    ) -> FeatureCollection:
        """
        Generic method to convert sql result to geojson. Geometry field is expected to be in geojson or postgis hex format.
        """
        exclude_properties.append(geometry_name)
        features = []
        for row in sql_result:
            dict_row = dict(row)
            features.append(
                Feature(
                    id=dict_row.get("gid") or dict_row.get("id") or 0,
                    geometry=geojsonloads(row[geometry_name])
                    if geometry_type == "geojson"
                    else wkbloads(row[geometry_name], hex=True),
                    properties=without_keys(dict_row, exclude_properties),
                )
            )
        return FeatureCollection(features)

    def calculate_single_isochrone(
        self, db: Session, *, obj_in: IsochroneSingle
    ) -> FeatureCollection:
        obj_in_data = jsonable_encoder(obj_in)
        sql = text(
            """
            SELECT gid, objectid, coordinates, ST_ASTEXT(ST_MAKEPOINT(coordinates[1], coordinates[2])) AS starting_point,
            step, speed::integer, modus, parent_id, sum_pois, ST_AsGeoJSON(geom) as geom
            FROM isochrones_api(:user_id,:scenario_id,:minutes,:x,:y,:n,:speed,:concavity,:modus,:routing_profile,NULL,NULL,NULL)
         """
        )
        result = db.execute(sql, obj_in_data)
        return self.sql_to_geojson(result, geometry_type="geojson")

    def calculate_multi_isochrones(
        self, db: Session, *, obj_in: IsochroneMulti
    ) -> FeatureCollection:
        obj_in_data = jsonable_encoder(obj_in)
        sql = text(
            """SELECT * FROM multi_isochrones_api(:user_id,:scenario_id,:minutes,:speed,:n,:routing_profile,:alphashape_parameter,:modus,:region_type,:region,:amenities)"""
        )
        result = db.execute(sql, obj_in_data)
        return self.sql_to_geojson(result)

    def count_pois_multi_isochrones(
        self, db: Session, *, obj_in: IsochroneMultiCountPois
    ) -> FeatureCollection:
        obj_in_data = jsonable_encoder(obj_in)
        sql = text(
            """SELECT row_number() over() AS gid, count_pois, region_name, geom FROM count_pois_multi_isochrones(:user_id,:scenario_id,:modus,:minutes,:speed,:region_type,:region,array[:amenities])"""
        )
        result = db.execute(sql, obj_in_data)
        return self.sql_to_geojson(result)

    def export_isochrone():
        pass


isochrone = CRUDIsochrone()
