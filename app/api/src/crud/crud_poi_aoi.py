from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import text

from src.db import models
from src.resources.enums import CalculationTypes, ReturnType, SQLReturnTypes


class CRUDPoiAoi:
    async def poi_aoi_visualization(
        self,
        db: AsyncSession,
        *,
        scenario_id: int,
        current_user: models.User,
        return_type: ReturnType
    ):
        _return_type = return_type.value
        if return_type == ReturnType.geobuf.value:
            _return_type = "db_geobuf"
        template_sql = SQLReturnTypes[_return_type].value
        sql = text(
            template_sql
            % """SELECT * FROM basic.poi_aoi_visualization(:user_id, :scenario_id, :active_upload_ids, :active_study_area_id)"""
        )
        result = await db.execute(
            sql,
            {
                "user_id": current_user.id,
                "scenario_id": scenario_id,
                "active_upload_ids": current_user.active_data_upload_ids,
                "active_study_area_id": current_user.active_study_area_id,
            },
        )
        return result.fetchall()[0][0]


poi_aoi = CRUDPoiAoi()
