from src.db.models.user import User
from .base import CRUDBase
from src.db.session import AsyncSession


class CRUDUser(CRUDBase):
    async def create(self, db: AsyncSession, id=None, obj_in: dict = None):
        if not obj_in and not id:
            raise ValueError("Either obj_in or id must be provided")

        if not obj_in:
            obj_in = User(id=id)
        return await super().create(db, obj_in=obj_in)

    async def get_first_user(self, db: AsyncSession):
        user = await db.execute(self.model.__table__.select().limit(1))
        return user.first()


user = CRUDUser(User)
