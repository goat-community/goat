from rich import print
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from sentry_sdk import capture_exception

from src import crud
from src.db import models
from src.db.session import async_session, staging_session


class DataImport():
    """"Imports prepared data into GOAT database."""
    def __init__(self):
        self.required_table_to_restore = [
            models.StudyArea,
            models.SubStudyArea,
            models.GridVisualization,
            models.GridCalculation,
            models.GridVisualizationParameter,
            models.StudyAreaGridVisualization,
            models.Node,
            models.Edge,
            models.Aoi,
            models.Poi,
            models.Building,
            models.Population,
        ]
        self.optional_table_to_restore = [
            models.ReachedEdgeHeatmap,
            models.ReachedEdgeHeatmapGridCalculation,
            models.ReachedPoiHeatmap,
            models.ReachedPoiHeatmapAccessibility,
        ]

    @staticmethod
    def object_as_dict(obj):
        return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

    async def import_table(self, table, db: AsyncSession, db_staging: AsyncSession) -> dict:

        table_empty = await crud.check_data.table_is_empty(db, table)

        # Check if target table exists and is empty
        if table_empty["Result"] != False and table_empty["Result"] != True:
            print(
                "[bold red]Error[/bold red]: Target table [bold magenta]%s[/bold magenta] does not exist."
                % table.__tablename__
            )
            return table_empty
        elif table_empty["Result"] == False:
            print(
                "[bold red]Error[/bold red]: There is data in table [bold magenta]%s[/bold magenta]. Data will not be uploaded."
                % table.__tablename__
            )
            return {"Error": "Table is not empty."}

        # Get all rows from source table
        print(
            "INFO: There is no default data for table [bold magenta]%s[/bold magenta]. Data will be uploaded."
            % table.__tablename__
        )
        rows = await db_staging.execute(select(table))

        # Check if there is an error with source table
        try:
            rows = await db_staging.execute(select(table))
        except Exception as e:
            capture_exception(e)
            print('[bold red]Error[/bold red]: There are no rows in table [bold magenta]%s[/bold magenta] in staging database.' % table.__tablename__)
            return 

        # Loop through rows and insert them into the database
        row_cnt = 0
        bulk_rows = []
        for row in rows.scalars():
            row_cnt += 1
            row_obj = self.object_as_dict(row)
            bulk_rows.append(table(**row_obj))

            if row_cnt % 10000 == 0:
                db.add_all(bulk_rows)
                await db.commit()
                print(
                    "    %s rows added to table [bold magenta]%s[/bold magenta]."
                    % (row_cnt, table.__tablename__)
                )
                bulk_rows = []
        # Add remaining rows to the database
        if bulk_rows != []:
            db.add_all(bulk_rows)
            await db.commit()
            print(
                "    %s rows added to table [bold magenta]%s[/bold magenta]."
                % (row_cnt, table.__tablename__)
            )

        await db.close()
        await db_staging.close()
        
        return {"msg": "Table imported"}

    async def import_all_tables(self, db: AsyncSession, db_staging: AsyncSession) -> dict:
        for table in self.required_table_to_restore:
            result = await self.import_table(table, db, db_staging)
            if result == None:
                print('[bold red]Error[/bold red]: Import stopped for table [bold magenta]%s[/bold magenta]. Bulk importing was stopped.' % table.__tablename__)
                return {"Error": "Problem in importing table."}
