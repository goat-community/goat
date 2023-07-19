from .base import CRUDBase
from src.db.models.layer import Layer


class CRUDLayer(CRUDBase):
    pass


layer = CRUDLayer(Layer)
