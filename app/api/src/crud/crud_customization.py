from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.crud.base import CRUDBase
from src.db import models


class CRUDCustomization(CRUDBase[models.Customization, models.Customization, models.Customization]):
    async def get_user_customization(
        self, db: AsyncSession, *, user_id: int
    ) -> List[models.UserCustomization]:
        db_obj = await db.execute(
            select(models.UserCustomization).filter(models.UserCustomization.user_id == user_id)
        )
        return db_obj.scalars().all()


customization = CRUDCustomization(models.Customization)
