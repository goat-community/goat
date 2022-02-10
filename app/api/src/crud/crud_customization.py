from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.db import models
from src.schemas.customization import CustomizationCreate, CustomizationUpdate


class CRUDCustomization(CRUDBase[models.Customization, CustomizationCreate, CustomizationUpdate]):
    async def insert_default_customization(
        self, db: AsyncSession, *, obj_in: CustomizationCreate
    ) -> models.Customization:

        db_obj = models.Customization(
            role_id=obj_in.role_id, type=obj_in.type, default_setting=obj_in.default_setting
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


customization = CRUDCustomization(models.Customization)
