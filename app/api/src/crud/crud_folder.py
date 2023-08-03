from .base import CRUDBase
from src.db.models.folder import Folder


class CRUDFolder(CRUDBase):
    pass


folder = CRUDFolder(Folder)
