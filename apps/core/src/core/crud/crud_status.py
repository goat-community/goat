from core.crud.base import CRUDBase
from core.db.models.status import Status


class CRUDStatus(CRUDBase):
    pass


status = CRUDStatus(Status)
