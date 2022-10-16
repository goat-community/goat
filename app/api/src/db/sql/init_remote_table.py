from alembic_utils.pg_extension import PGExtension
from psycopg2.errors import DuplicateObject
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError

from src.core.config import settings
from src.db.session import legacy_engine

# postgres_fdw_sql = "CREATE EXTENSION postgres_fdw"


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
    create_foreign_server = """
        CREATE SERVER foreign_server
        FOREIGN DATA WRAPPER postgres_fdw
        OPTIONS (host :host, port :port, dbname :dbname);
        """
    values = {
        "host": settings.POSTGRES_SERVER_RAW,
        "port": "5432",
        "dbname": settings.POSTGRES_DB_RAW,
    }
    create_foreign_server = text(create_foreign_server)
    try:
        legacy_engine.execute(create_foreign_server, values)
    except ProgrammingError as exception:
        if exception.orig.pgcode == "42710":
            print(exception.orig)


def downgrade_foreign_server():
    drop_foreign_server = text("DROP SERVER IF EXISTS :foreign_server;")
    values = {"foreign_server": "foreign_server"}
    legacy_engine.execute(drop_foreign_server, values)


# TODO local_user and foreign_server should pass dynamicly.
# But the execute method adds quotes around them which should not for postgreSQL.


def upgrade_mapping_user():
    create_mapping_user = """CREATE USER MAPPING FOR postgres
                            SERVER foreign_server
                            OPTIONS (user :mapping_user, password :password);"""
    create_mapping_user = text(create_mapping_user)
    values = {
        "local_user": settings.POSTGRES_USER,
        "foreign_server": "foreign_server",
        "mapping_user": "mapping_user",
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
    drop_mapping_user = text("DROP USER MAPPING IF EXISTS FOR mapping_user SERVER foreign_server;")
    values = {"mapping_user": "mapping_user", "foreign_server": "foreign_server"}
    legacy_engine.execute(drop_mapping_user, values)
