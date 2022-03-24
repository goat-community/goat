import os
import subprocess

from rich import print
from sqlalchemy.sql import select, text

from src.db import models
from src.db.session import sync_session
from src.utils import print_hashtags, print_info, print_warning


class DataImport:
    """Imports prepared data into GOAT database. This script is only for development purposes and should not be used in production."""

    def __init__(self, db):
        self.models_basic_schema = [
            models.StudyArea,
            models.SubStudyArea,
            models.GridVisualization,
            models.GridCalculation,
            models.StudyAreaGridVisualization,
            models.Node,
            models.Edge,
            models.Aoi,
            models.Poi,
            models.Building,
            models.Population,
        ]
        self.db = db
        # self.optional_table_to_restore = [
        #     models.ReachedEdgeHeatmap,
        #     models.ReachedEdgeHeatmapGridCalculation,
        #     models.ReachedPoiHeatmap,
        #     models.ReachedPoiHeatmapAccessibility,
        # ]

    # Create pgpass function
    def create_pgpass(self):
        db_name = os.getenv("COMPOSE_PROJECT_NAME")
        try:
            os.system(f"rm /tmp/.pgpass")
        except:
            pass
        os.system(
            "echo "
            + ":".join(
                [
                    os.getenv("POSTGRES_SERVER"),
                    os.getenv("POSTGRES_OUTER_PORT"),
                    os.getenv("COMPOSE_PROJECT_NAME"),
                    os.getenv("POSTGRES_USER"),
                    os.getenv("POSTGRES_PASSWORD"),
                ]
            )
            + f" > /tmp/.pgpass"
        )
        os.system(f"chmod 600  /tmp/.pgpass")

    def restore_qualified_dumps(self):
        """Finds dump files that correspond to a table name."""
        basic_table_names = [i.__tablename__ for i in self.models_basic_schema]
        dump_files = []

        for file in os.listdir("/app/src/data"):
            file_name = file.split(".")[0]
            if file.endswith(".sql") and file_name in basic_table_names:
                dump_files.append(file_name)

        if dump_files == []:
            print_warning(
                f"No dump files were found. Please make sure that you have prepared the data in the correct format."
            )
            return {
                "msg": "No dump files were found. Please make sure that you have prepared the data in the correct format."
            }
        else:
            self.create_pgpass()
            db_name = os.getenv("COMPOSE_PROJECT_NAME")
            password = os.getenv("POSTGRES_PASSWORD")

        for basic_tbl in basic_table_names:
            if basic_tbl in dump_files:
                print_info(f"Dump file [bold magenta]{basic_tbl}[/bold magenta] will be restored.")
                clean_sql_table = f"""
                TRUNCATE TABLE basic.{basic_tbl} CASCADE;
                ALTER SEQUENCE IF EXISTS basic.{basic_tbl}_id_seq RESTART WITH 1;"""
                self.db.execute(text(clean_sql_table))
                self.db.commit()
                self.db.close()

                subprocess.run(
                    f"PGPASSWORD={password} psql -h {os.getenv('POSTGRES_SERVER')} -U {os.getenv('POSTGRES_USER')} -d {db_name} -f /app/src/data/{basic_tbl}.sql",
                    shell=True,
                    check=True,
                )
                    
            else:
                print_warning(
                    f"No dump file was found for table [bold magenta]{basic_tbl}[/bold magenta]. Please make sure that you have prepared all the needed data."
                )


db = sync_session()
DataImport(db).restore_qualified_dumps()
