from xmlrpc.client import Boolean

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.db.models.customer.customization import Customization as CustomizationDB
from app.db.models.customer.role import Role as RoleDB
from app.schemas.customization import CustomizationCreate, CustomizationUpdate


class CRUDCustomization(CRUDBase[CustomizationDB, CustomizationCreate, CustomizationUpdate]):
    async def insert_default_customization(self, db: AsyncSession, *, obj_in: CustomizationCreate) -> CustomizationDB:    
        
        #role = await db.execute(select(RoleDB))
        #role_id = role.fetchone()

        db_obj = CustomizationDB(
            role_id = {"superuser": 1, "user": 2}[obj_in.role_name],
            type = obj_in.type,
            default_setting = obj_in.default_setting
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
            

customization = CRUDCustomization(CustomizationDB)
