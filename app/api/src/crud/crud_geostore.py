from src.crud.base import CRUDBase
from src.db import models


class CRUDGeostore(CRUDBase[models.Geostore, models.Geostore, models.Geostore]):
    pass


geostore = CRUDGeostore(models.Geostore)

