from sqlalchemy import MetaData, Table
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.schema import DropTable

from src.crud.base import CRUDBase
from src.db import models


class CRUDStaticLayer(CRUDBase[models.StaticLayer, models.StaticLayer, models.StaticLayer]):
    async def drop_postgis_table(self, db: AsyncSession, table_name: str):
        metadata_obj = MetaData(schema="extra")
        table = Table(table_name, metadata_obj)
        await db.execute(DropTable(table, if_exists=True))

    pass


static_layer = CRUDStaticLayer(models.StaticLayer)
