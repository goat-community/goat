from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import text
from fastapi.encoders import jsonable_encoder
from src.db import models
from src.schemas.poi_aoi import POIAOIVisualization
from src.resources.enums import SQLReturnTypes

class CRUDPoiAoi:
    async def poi_aoi_visualization(
        self, db: AsyncSession, *, obj_in: POIAOIVisualization, current_user: models.User, return_type: str = 'geojson'
    ):
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data["user_id"] = current_user.id

        if return_type in SQLReturnTypes._member_names_:
            template_sql = SQLReturnTypes[return_type].value

        sql = text(template_sql % 
            """SELECT * FROM basic.poi_aoi_visualization(:user_id, :scenario_id, :amenities, :modus, :active_upload_ids, :active_study_area_id)"""
        )
        result = await db.execute(sql, obj_in_data)
        return result.fetchall()[0][0] 


poi_aoi = CRUDPoiAoi()
