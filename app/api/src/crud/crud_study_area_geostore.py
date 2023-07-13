
from src.crud.base import CRUDBase
from src.db import models



class CRUDStudyAreaGeostore(CRUDBase[models.StudyAreaGeostore, models.StudyAreaGeostore, models.StudyAreaGeostore]):
    pass

study_area_geostore = CRUDStudyAreaGeostore(models.StudyAreaGeostore)
