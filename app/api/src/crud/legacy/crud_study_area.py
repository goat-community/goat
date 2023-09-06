from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.db import models

from .base import ModelType
from .crud_study_area_geostore import study_area_geostore as crud_study_area_geostore


class CRUDStudyArea(CRUDBase[models.StudyArea, models.StudyArea, models.StudyArea]):
    async def get_first(self, db: AsyncSession) -> ModelType:
        all_study_areas = await self.get_all(db=db)
        if all_study_areas:
            return all_study_areas[0]
        else:
            return None

    async def add_geostore_to_study_area(
        self, db: AsyncSession, study_area_id: int, geostore_id: int
    ):
        study_area_geostore = models.StudyAreaGeostore(
            study_area_id=study_area_id, geostore_id=geostore_id
        )

        return await crud_study_area_geostore.create(db, obj_in=study_area_geostore)


study_area = CRUDStudyArea(models.StudyArea)
