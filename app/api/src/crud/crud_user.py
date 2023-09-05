from src.db.models.user import User
from .base import CRUDBase


class CRUDUser(CRUDBase):
    pass


user = CRUDUser(User)
