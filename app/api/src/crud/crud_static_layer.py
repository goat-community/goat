from sqlalchemy import MetaData, Table

from src.crud.base import CRUDBase
from src.db import models


class CRUDStaticLayer(CRUDBase[models.StaticLayer, models.StaticLayer, models.StaticLayer]):
    async def drop_postgis_table(self, db, table_name):
        metadata_obj = MetaData(schema="extra")
        table = Table(table_name, metadata_obj)
        await table.drop(db)

    pass


static_layer = CRUDStaticLayer(models.StaticLayer)
