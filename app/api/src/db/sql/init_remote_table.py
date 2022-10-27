from typing import Union

from alembic_utils.pg_extension import PGExtension
from psycopg2.errors import DuplicateObject
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError

from src.core.config import settings
from src.db.session import legacy_engine

# postgres_fdw_sql = "CREATE EXTENSION postgres_fdw"

FOREIGN_SERVER = "foreign_server"


def upgrade_postgres_fdw():
    postgres_fdw = PGExtension(schema="public", signature="postgres_fdw")
    statement = postgres_fdw.to_sql_statement_create()
    try:
        legacy_engine.execute(text(statement.text))
    except ProgrammingError as exception:
        if exception.orig.pgcode == "42710":
            print("FWD Extension already exists on database.")


def downgrade_postgres_fdw():
    postgres_fdw = PGExtension(schema="public", signature="postgres_fdw")
    statement = postgres_fdw.to_sql_statement_drop()
    legacy_engine.execute(text(statement.text))


def upgrade_foreign_server():
    create_foreign_server = text(
        f"""
        CREATE SERVER {FOREIGN_SERVER}
        FOREIGN DATA WRAPPER postgres_fdw
        OPTIONS (host :host, port :port, dbname :dbname);
        """
    )
    values = {
        "host": settings.POSTGRES_SERVER_RAW,
        "port": settings.POSTGRES_OUTER_PORT_RAW,
        "dbname": settings.POSTGRES_DB_RAW,
    }
    try:
        legacy_engine.execute(create_foreign_server, values)
    except ProgrammingError as exception:
        if exception.orig.pgcode == "42710":
            print(exception.orig)


def downgrade_foreign_server():
    drop_foreign_server = text(f"DROP SERVER IF EXISTS {FOREIGN_SERVER};")
    values = {"foreign_server": "foreign_server"}
    legacy_engine.execute(drop_foreign_server, values)


# TODO local_user and foreign_server should pass dynamicly.
# But the execute method adds quotes around them which should not for postgreSQL.


def upgrade_mapping_user():
    create_mapping_user = text(
        f"""CREATE USER MAPPING FOR {settings.POSTGRES_USER}
                            SERVER {FOREIGN_SERVER}
                            OPTIONS (user :server_user, password :password);"""
    )
    values = {
        "server_user": settings.POSTGRES_USER,
        "password": settings.POSTGRES_PASSWORD_RAW,
    }
    try:
        legacy_engine.execute(create_mapping_user, values)
    except ProgrammingError as exception:
        if exception.orig.pgcode == "42710":
            print(exception.orig)


# TODO: the mapping_user and foreign_server should get dynamicly passed.
# The problem is the same as upgrade function.


def downgrade_mapping_user():
    drop_mapping_user = text(
        f"DROP USER MAPPING IF EXISTS FOR {settings.POSTGRES_USER} SERVER {FOREIGN_SERVER};"
    )
    legacy_engine.execute(drop_mapping_user)


def upgrade_schema(schema_name: str):
    create_foreign_schema = f"CREATE SCHEMA IF NOT EXISTS {schema_name};"
    legacy_engine.execute(text(create_foreign_schema))


def downgrade_schema(schema_name: str):
    drop_foreign_schema = f"DROP SCHEMA IF EXISTS {schema_name};"
    legacy_engine.execute(text(drop_foreign_schema))


def upgrade_foreign_tables(foreign_tables: list[str], foreign_schema):
    mapping_schema_name = "foreign_" + foreign_schema
    upgrade_schema(mapping_schema_name)
    create_foreign_table = f"""IMPORT FOREIGN SCHEMA {foreign_schema} LIMIT TO ({','.join(foreign_tables)})
    FROM SERVER {FOREIGN_SERVER} INTO {mapping_schema_name};"""
    legacy_engine.execute(text(create_foreign_table))


def downgrade_foreign_table(table_name: Union[str, list[str]], foreign_schema):
    if type(table_name) == str:
        table_names = [table_name]
    else:
        table_names = table_name
    for table_name in table_names:
        mapping_schema_name = "foreign_" + foreign_schema
        full_table_name = f"{mapping_schema_name}.{table_name}"
        drop_foreign_table = text(f"""DROP FOREIGN TABLE IF EXISTS {full_table_name};""")

        legacy_engine.execute(drop_foreign_table)


if __name__ == "__main__":
    # downgrade_foreign_table(["node", "study_area"], "basic")
    downgrade_schema("foreign_basic")
