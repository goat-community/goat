from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import text
from src.db import models
from src.resources.enums import CalculationTypes, SQLReturnTypes, ReturnType

class CRUDPoiAoi:
    async def poi_aoi_visualization(
        self, db: AsyncSession, *, 
        scenario_id: int, 
        modus: CalculationTypes, 
        current_user: models.User, 
        return_type: ReturnType 
    ):
        template_sql = SQLReturnTypes[return_type.value].value

        sql = text(template_sql % 
            """SELECT * FROM basic.poi_aoi_visualization(:user_id, :scenario_id, :modus, :active_upload_ids, :active_study_area_id)"""
        )
        result = await db.execute(sql, 
            {
                "user_id": current_user.id, 
                "scenario_id": scenario_id, 
                "modus": modus.value, 
                "active_upload_ids": current_user.active_data_upload_ids, 
                "active_study_area_id": current_user.active_study_area_id
            }
        )
        return result.fetchall()[0][0] 

poi_aoi = CRUDPoiAoi()
