from src.crud.base import CRUDBase
from src.db import models

class CRUDSystem(CRUDBase[models.System, models.System, models.System]):
    pass

system = CRUDSystem(models.System)
