from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.db import models


class CRUDCustomization(CRUDBase[models.Customization, models.Customization, models.Customization]):
    pass 

customization = CRUDCustomization(models.Customization)
