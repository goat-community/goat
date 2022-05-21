from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud, schemas
from src.db import models
from src.tests.utils.utils import random_lower_string


async def create_random_organization(*, db: AsyncSession) -> models.Organization:
    name = random_lower_string()
    organization_in = schemas.OrganizationCreate(name=name)
    organization = await crud.organization.create(db, obj_in=organization_in)
    return organization
