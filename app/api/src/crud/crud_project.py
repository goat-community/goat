from .base import CRUDBase
from src.db.models.project import Project


class CRUDProject(CRUDBase):
    pass


project = CRUDProject(Project)
