from src.crud.base import CRUDBase
from src.db import models


class CRUDStaticLayer(CRUDBase[models.StaticLayer, models.StaticLayer, models.StaticLayer]):
    pass


static_layer = CRUDStaticLayer(models.StaticLayer)
