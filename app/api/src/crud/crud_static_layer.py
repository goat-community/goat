from sqlalchemy import Column, MetaData, String, Table, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.schema import DropTable

from src.crud.base import CRUDBase
from src.db import models


class CRUDStaticLayer(CRUDBase[models.StaticLayer, models.StaticLayer, models.StaticLayer]):
    async def drop_postgis_table(self, db: AsyncSession, table_name: str):
        metadata_obj = MetaData(schema="extra")
        table = Table(table_name, metadata_obj)
        await db.execute(DropTable(table, if_exists=True))

    async def list_static_layer_table_names(self, db: AsyncSession, name_like=""):
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


static_layer = CRUDStaticLayer(models.StaticLayer)
