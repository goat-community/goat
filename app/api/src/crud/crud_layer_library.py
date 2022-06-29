from src.crud.base import CRUDBase
from src.db import models
from src.db.models import layer_library
from src.schemas.organization import OrganizationCreate, OrganizationUpdate


class CRUDLayerLibrary(CRUDBase[models.LayerLibrary, models.LayerLibrary, models.LayerLibrary]):
    pass


layer_library = CRUDLayerLibrary(models.LayerLibrary)


class CRUDStyleLibrary(CRUDBase[models.StyleLibrary, models.StyleLibrary, models.StyleLibrary]):
    pass


style_library = CRUDStyleLibrary(models.StyleLibrary)
