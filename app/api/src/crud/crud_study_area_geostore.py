from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.db import models

from .base import ModelType


class CRUDStudyAreaGeostore(CRUDBase[models.StudyAreaGeostore, models.StudyAreaGeostore, models.StudyAreaGeostore]):
    pass

study_area_geostore = CRUDStudyAreaGeostore(models.StudyAreaGeostore)
