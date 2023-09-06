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
    ):
        _return_type = return_type.value
        if return_type == ReturnType.geobuf.value:
            _return_type = "db_geobuf"
        template_sql = SQLReturnTypes[_return_type].value

        attributes = 'uid, id, category, name, geom, opening_hours, street, housenumber, zipcode, edit_type'

        query = f"""
        SELECT {attributes}, NULL as grouped
        FROM basic.poi_aoi_visualization(:user_id, :scenario_id, :active_upload_ids, :active_study_area_id, FALSE)
        UNION ALL
        SELECT NULL AS uid, row_number() over() AS id, category, name, ST_CENTROID(ST_COLLECT(ST_ClusterWithin(geom, 0.001))) AS geom,
        NULL, NULL, NULL, NULL, NULL, true
        FROM basic.poi_aoi_visualization(:user_id, :scenario_id, :active_upload_ids, :active_study_area_id, TRUE)
        GROUP BY category, name
        """
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
                "active_study_area_id": current_user.active_study_area_id
            },
        )
        return result.fetchall()[0][0]


poi_aoi = CRUDPoiAoi()
