from sqlalchemy import Column, MetaData, String, Table, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.schema import DropTable

from src.crud.base import CRUDBase
from src.db import models
from src.utils import tablify


class CRUDStaticLayer(CRUDBase[models.StaticLayer, models.StaticLayer, models.StaticLayer]):
    async def drop_postgis_table(self, db: AsyncSession, table_name: str):
        metadata_obj = MetaData(schema="extra")
        table = Table(table_name, metadata_obj)
        await db.execute(DropTable(table, if_exists=True))

    async def list_static_layer_table_names(self, db: AsyncSession, name_like: str = ""):
        metadata_obj = MetaData(schema="information_schema")
        tables = Table(
            "tables",
            metadata_obj,
            Column("table_name", String()),
            Column("table_schema", String()),
        )
        query = select(tables).where(tables.columns.table_name.like(name_like + "%"))
        result = await db.execute(query)
        tables = result.scalars().all()
        return tables

    async def uniquify_static_layer_name(self, db: AsyncSession, file_name: str):
        original_name = file_name.split(".")[0]
        original_name = tablify(original_name)
        name = original_name
        static_layer_table_names = await self.list_static_layer_table_names(db=db, name_like=name)
        counter = 1
        while name in static_layer_table_names:
            name = f"{original_name}_{counter}"
            counter += 1

        return name


static_layer = CRUDStaticLayer(models.StaticLayer)
