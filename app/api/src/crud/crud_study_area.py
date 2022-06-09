from typing import Any, List

from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.db import models

from .base import ModelType


class CRUDStudyArea(CRUDBase[models.StudyArea, models.StudyArea, models.StudyArea]):
    async def get_first(self, db: AsyncSession) -> ModelType:
        all_study_areas = await self.get_all(db=db)
        if all_study_areas:
            return all_study_areas[0]
        else:
            return None


study_area = CRUDStudyArea(models.StudyArea)
