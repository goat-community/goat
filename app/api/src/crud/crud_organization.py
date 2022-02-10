from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.db import models
from src.schemas.organization import OrganizationCreate, OrganizationUpdate


class CRUDOrganization(CRUDBase[models.Organization, OrganizationCreate, OrganizationUpdate]):
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[models.Organization]:
        result = await db.execute(
            select(models.Organization).filter(models.Organization.name == name)
        )
        return result.scalars().first()


organization = CRUDOrganization(models.Organization)
