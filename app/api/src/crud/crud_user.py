from src.db.models.user import User
from .base import CRUDBase
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from src.utils import table_exists

class CRUDUser(CRUDBase):
    async def create_user_data_tables(self, async_session: AsyncSession, user_id: UUID):
        """Create the user data tables."""

        for table_type in ["point", "line", "polygon"]:
            table_name = f"{table_type}_{str(user_id).replace('-', '')}"

            # Check if table exists
            if not await table_exists(async_session, table_name):
                # Create table
                sql_create_table = f"""
                CREATE TABLE user_data."{table_name}" (
                    id SERIAL PRIMARY KEY,
                    layer_id UUID NOT NULL REFERENCES customer.layer(id),
                    geom GEOMETRY,
                    {', '.join([f'integer_attr{i+1} INTEGER' for i in range(15)])},
                    {', '.join([f'bigint_attr{i+1} INTEGER' for i in range(5)])},
                    {', '.join([f'float_attr{i+1} FLOAT' for i in range(10)])},
                    {', '.join([f'text_attr{i+1} TEXT' for i in range(20)])},
                    {', '.join([f'datetime_attr{i+1} TIMESTAMP' for i in range(3)])}
                );
                """
                await async_session.execute(text(sql_create_table))
                # Create GIST Index
                await async_session.execute(text(f"""CREATE INDEX ON user_data."{table_name}" USING GIST(geom);"""))
                # Create Index on ID
                await async_session.execute(text(f"""CREATE INDEX ON user_data."{table_name}" (id);"""))

            else:
                print(f"Table '{table_name}' already exists.")

        # Commit changes
        await async_session.commit()

    async def delete_user_data_tables(self, async_session: AsyncSession, user_id: UUID):
        """Delete the user data tables."""

        for table_type in ["point", "line", "polygon"]:
            table_name = f"{table_type}_{str(user_id).replace('-', '')}"

            # Check if table exists
            if await table_exists(async_session, table_name):
                sql_delete_table = f"""
                DROP TABLE IF EXISTS user_data."{table_name}";
                """
                await async_session.execute(text(sql_delete_table))
            else:
                print(f"Table '{table_name}' does not exist.")
        await async_session.commit()


user = CRUDUser(User)
