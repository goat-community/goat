from src.crud.base import CRUDBase
from src.db import models


class CRUDStudyArea(CRUDBase[models.StudyArea, models.StudyArea, models.StudyArea]):
    pass


study_area = CRUDStudyArea(models.StudyArea)
