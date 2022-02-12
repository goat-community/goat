from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.db import models
from src.schemas.organization import OrganizationCreate, OrganizationUpdate


class CRUDOrganization(CRUDBase[models.Organization, OrganizationCreate, OrganizationUpdate]):
    pass


organization = CRUDOrganization(models.Organization)
