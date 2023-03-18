from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import text

from src.db import models
from src.resources.enums import ReturnType, SQLReturnTypes


class CRUDPoiAoi:
    async def poi_aoi_visualization(
        self,
        db: AsyncSession,
        *,
        scenario_id: int,
        current_user: models.User,
        return_type: ReturnType,
        full_attributes: bool = True,
        grouped_multi_entrance: bool = False,
    ):
        _return_type = return_type.value
        if return_type == ReturnType.geobuf.value:
            _return_type = "db_geobuf"
        template_sql = SQLReturnTypes[_return_type].value

        if full_attributes == True:
            attributes = '*'
        else:
            attributes = 'id, category, name, geom'


        if grouped_multi_entrance == True:
            query = """SELECT row_number() over() AS id, category, name, ST_CENTROID(ST_COLLECT(geom)) AS geom 
            FROM basic.poi_aoi_visualization(:user_id, :scenario_id, :active_upload_ids, :active_study_area_id, :grouped_multi_entrance)
            GROUP BY category, name"""
        else: 
            query = f"""SELECT {attributes} 
            FROM basic.poi_aoi_visualization(:user_id, :scenario_id, :active_upload_ids, :active_study_area_id, :grouped_multi_entrance)"""
            
        sql = text(
            template_sql
            % query
        )
        result = await db.execute(
            sql,
            {
                "user_id": current_user.id,
                "scenario_id": scenario_id,
                "active_upload_ids": current_user.active_data_upload_ids,
                "active_study_area_id": current_user.active_study_area_id,
                "grouped_multi_entrance": grouped_multi_entrance,
            },
        )
        return result.fetchall()[0][0]


poi_aoi = CRUDPoiAoi()
