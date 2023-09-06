from typing import List

from sqlalchemy.future import select
from sqlalchemy.orm import Session

from src.crud.base import CRUDBase
from src.db import models


class CRUDLayerLibrary(CRUDBase[models.LayerLibrary, models.LayerLibrary, models.LayerLibrary]):

    # Used Session in order to use in validator
    def get_all_layer_names(self, db: Session) -> List[str]:
        statement = select(self.model.name)
        layers = db.execute(statement)
        layers = layers.scalars().all()
        return layers


layer_library = CRUDLayerLibrary(models.LayerLibrary)


class CRUDStyleLibrary(CRUDBase[models.StyleLibrary, models.StyleLibrary, models.StyleLibrary]):
    pass


style_library = CRUDStyleLibrary(models.StyleLibrary)
