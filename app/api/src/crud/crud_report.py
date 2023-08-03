from .base import CRUDBase
from src.db.models.report import Report


class CRUDReport(CRUDBase):
    pass


report = CRUDReport(Report)
