from src import schemas
from src.crud.base import CRUDBase
from src.db import models


class CRUDRole(CRUDBase[models.Role, schemas.RoleCreate, schemas.RoleUpdate]):
    pass


role = CRUDRole(models.Role)
