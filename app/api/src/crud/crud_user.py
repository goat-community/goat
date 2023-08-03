from src.db.models.user import User
from .base import CRUDBase
from src.db.session import AsyncSession


class CRUDUser(CRUDBase):
    pass


user = CRUDUser(User)
