from src.crud.base import CRUDBase
from src.db import models
from src.schemas.organization import OrganizationCreate, OrganizationUpdate


class CRUDOrganization(CRUDBase[models.Organization, OrganizationCreate, OrganizationUpdate]):
    pass


organization = CRUDOrganization(models.Organization)
