from .base import CRUDBase
from src.db.models.content import Content


class CRUDContent(CRUDBase):
    pass


content = CRUDContent(Content)
