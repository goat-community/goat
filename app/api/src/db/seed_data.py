import os
import subprocess
import asyncio
import sys
from rich import print
from sqlalchemy.sql import select, text

from src.db import models
from src.db.session import sync_session
from src.utils import print_info, print_warning
from src.core.config import Settings
from src.resources.enums import UpdateTableFunction


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


class DataUpdate:
    """Updates the data of a live database."""

    def __init__(self, db):
        self.settings_env = Settings()
        self.db = db

    def connect_fdw(self):
        """Connects the FDW."""
        fdw_connections = self.db.execute(
            text(
                """
                SELECT * FROM postgres_fdw_get_connections()
                """
            )
        )

        fdw_connections = fdw_connections.all()
        fdw_connections = [i[0] for i in fdw_connections]
        if "update_bridge" in fdw_connections:
            print_info("FDW connection already exists but will be recreated.")
            self.db.execute(text("SELECT postgres_fdw_disconnect('update_bridge');"))

        self.db.execute(
            text(
                f"""
            CREATE SERVER IF NOT EXISTS update_bridge
            FOREIGN DATA WRAPPER postgres_fdw
            OPTIONS (host :staging_host, dbname :staging_db);

            CREATE USER MAPPING IF NOT EXISTS FOR {self.settings_env.POSTGRES_USER}
            SERVER update_bridge
            OPTIONS (user :staging_user, password :password);

            DROP SCHEMA IF EXISTS temporal CASCADE;
            CREATE SCHEMA temporal;
            IMPORT FOREIGN SCHEMA basic
            FROM SERVER update_bridge INTO temporal;

            IMPORT FOREIGN SCHEMA customer
            FROM SERVER update_bridge INTO temporal;
            """
            ),
            {
                "staging_host": self.settings_env.POSTGRES_SERVER_STAGING,
                "staging_db": self.settings_env.POSTGRES_DB_STAGING,
                "staging_user": self.settings_env.POSTGRES_USER_STAGING,
                "password": self.settings_env.POSTGRES_PASSWORD_STAGING,
            },
        )
        self.db.commit()

    def update_opportunity_config(self):
        """Updates the opportunity config tables."""
        # Update opportunity configs
        self.db.execute(
            text(
                """
            DELETE FROM basic.opportunity_default_config;
            DELETE FROM basic.opportunity_study_area_config;
            DELETE FROM basic.opportunity_group;

            INSERT INTO basic.opportunity_group
            SELECT * 
            FROM temporal.opportunity_group;

            INSERT INTO basic.opportunity_default_config
            SELECT * 
            FROM temporal.opportunity_default_config;

            INSERT INTO basic.opportunity_study_area_config
            SELECT *
            FROM temporal.opportunity_study_area_config;
            """
            )
        )
        self.db.commit()

    def update_layer_library(self):
        # Update layer configs
        self.db.execute(
            text(
                """
            DELETE FROM customer.layer_library;
            DELETE FROM customer.style_library;
            DELETE FROM customer.layer_source;
            
            INSERT INTO customer.layer_source
            SELECT *
            FROM temporal.layer_source;
            
            INSERT INTO customer.style_library
            SELECT *
            FROM temporal.style_library;

            INSERT INTO customer.layer_library
            SELECT *
            FROM temporal.layer_library;
            """
            )
        )
        self.db.commit()

    def update_customization(self):
        # Update customization
        self.db.execute(
            text(
                """
            DELETE FROM customer.customization;
            INSERT INTO customer.customization(type, setting, role_id)
            SELECT type, setting, cr.id
            FROM temporal.customization c, temporal.role tr, customer.role cr
            WHERE tr.name = cr.name
            AND c.role_id = tr.id;
            """
            )
        )
        self.db.commit()

    def update_aoi(self):
        """Updates the AOI table."""
        self.db.execute(
            text(
                """
                TRUNCATE basic.aoi;
                INSERT INTO basic.aoi 
                SELECT * FROM temporal.aoi;
                """
            )
        )
        self.db.commit()

    def update_poi(self):
        """Updates the POI table."""
        self.db.execute(
            text(
                """
                TRUNCATE TABLE basic.poi;
                INSERT INTO basic.poi
                SELECT * FROM temporal.poi; 
                """
            )
        )
        self.db.commit()

        self.db.execute(
            text(
                """
                WITH scenario_features_corrupted AS (
                    SELECT m.uid 
                    FROM (
                        SELECT * 
                        FROM customer.poi_modified 
                        WHERE data_upload_id IS NULL 
                        AND edit_type IN ('m', 'd')
                    ) m
                    LEFT JOIN temporal.poi p 
                    ON m.uid = p.uid 
                    WHERE p.uid IS NULL
                )
                UPDATE temporal.poi_modified p
                SET outdated = True
                FROM scenario_features_corrupted c
                WHERE p.uid = c.uid;
                """
            )
        )
        self.db.commit()

    def update_table_groups(self, db, table_groups: list[str]):
        """Updates the table groups."""
        for table_group in table_groups:
            if table_group not in UpdateTableFunction.__members__:
                print_warning(f"Table group {table_group} is not supported.")
                sys.exit()

        db = sync_session()
        data_update = DataUpdate(db)

        for table_group in UpdateTableFunction:
            if (
                table_group.name in table_groups
                or (table_groups[0] == UpdateTableFunction.all.name and len(table_groups) == 1)
            ) and table_group.name != UpdateTableFunction.all:

                print_info("Updating %s table group." % table_group.name)
                function_to_call = getattr(data_update, table_group.value)
                function_to_call()


# def main():
#     from src.db.session import sync_session

#     db = sync_session()
#     data_update = DataUpdate(db)
#     data_update.connect_fdw()
#     data_update.update_table_groups(db, ["poi"])
# main()

# TODO: Ways
# TODO: Buildings and Population
# TODO: Tables in Extra Schema
# TODO: Heatmap