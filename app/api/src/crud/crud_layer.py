from .base import CRUDBase
from src.db.models.layer import Layer, LayerBase


class CRUDLayer(CRUDBase):
    pass


layer = CRUDLayer(Layer)
