import time
from typing import Union

from alembic_utils.pg_extension import PGExtension
from engines import chapar_engine, chapar_uri
from sqlalchemy import text
from sqlalchemy.engine import create_engine
from sqlalchemy.exc import ProgrammingError

from src.core.config import settings

FOREIGN_SERVER = "foreign_server"


def upgrade_extension(extenstion_name:str, db_uri:str=chapar_uri):
    if db_uri:
        legacy_engine = create_engine(db_uri,future=False)
    extension = PGExtension(schema="public", signature=extenstion_name)
    statement = extension.to_sql_statement_create()
    try:
        legacy_engine.execute(text(statement.text))
    except ProgrammingError as exception:
        if exception.orig.pgcode == "42710":
            print(f"{extenstion_name} Extension already exists on database.")
    

def upgrade_postgres_fdw(db_uri:str = chapar_uri):
    upgrade_extension('postgres_fdw',db_uri)


def downgrade_postgres_fdw():
    postgres_fdw = PGExtension(schema="public", signature="postgres_fdw")
    statement = postgres_fdw.to_sql_statement_drop()
    chapar_engine.execute(text(statement.text))


def upgrade_foreign_server(
    foreign_server: str = settings.POSTGRES_DB_RAW,
    host: str = settings.POSTGRES_SERVER_RAW,
    port: Union[str, int] = settings.POSTGRES_OUTER_PORT_RAW,
    dbname: str = settings.POSTGRES_DB_RAW,
    db_uri: str = chapar_uri,
):
    create_foreign_server = text(
        f"""
        CREATE SERVER {foreign_server}
        FOREIGN DATA WRAPPER postgres_fdw
        OPTIONS (host :host, port :port, dbname :dbname);
        """
    )
    values = {
        "host": host,
        "port": str(port),
        "dbname": dbname,
    }
    chapar_engine.execute(create_foreign_server, values)


def downgrade_foreign_server():
    drop_foreign_server = text(f"DROP SERVER IF EXISTS {FOREIGN_SERVER};")
    values = {"foreign_server": "foreign_server"}
    chapar_engine.execute(drop_foreign_server, values)


# TODO local_user and foreign_server should pass dynamicly.
# But the execute method adds quotes around them which should not for postgreSQL.


def upgrade_mapping_user(
    foreign_server: str = settings.POSTGRES_DB_RAW,
    local_user: str = settings.POSTGRES_USER,
    server_user: str = settings.POSTGRES_USER_RAW,
    password: str = settings.POSTGRES_PASSWORD_RAW,
    db_uri: str = chapar_uri,
):
    if db_uri:
        legacy_engine = create_engine(db_uri, future=False)
    create_mapping_user = text(
        f"""CREATE USER MAPPING FOR {local_user}
                            SERVER {foreign_server}
                            OPTIONS (user :server_user, password :password);"""
    )
    values = {"server_user": server_user, "password": password}
    legacy_engine.execute(create_mapping_user, values)


# TODO: the mapping_user and foreign_server should get dynamicly passed.
# The problem is the same as upgrade function.


def downgrade_mapping_user():
    drop_mapping_user = text(
        f"DROP USER MAPPING IF EXISTS FOR {settings.POSTGRES_USER} SERVER {FOREIGN_SERVER};"
    )
    chapar_engine.execute(drop_mapping_user)


def mapping_schema_name_generator(foreign_schema: str, foreign_server: str):
    return "foreign_" + foreign_schema + "_" + foreign_server


def upgrade_schema(schema_name: str,
                    db_uri: str=None):
    if db_uri:
        legacy_engine = create_engine(db_uri,future=False)
    create_foreign_schema = f"CREATE SCHEMA IF NOT EXISTS {schema_name};"
    chapar_engine.execute(text(create_foreign_schema))


def downgrade_schema(schema_name: str = None,
                     db_uri: str=None):
    if db_uri:
        legacy_engine = create_engine(db_uri,future=False)
    drop_foreign_schema = f"DROP SCHEMA IF EXISTS {schema_name};"
    legacy_engine.execute(text(drop_foreign_schema))


def upgrade_foreign_tables(
    foreign_tables: Union[str, list[str]]=None,
    foreign_schema: str = None,
    foreign_server: str = settings.POSTGRES_DB_RAW,
    db_uri: str = None
):
    if db_uri:
        legacy_engine = create_engine(db_uri,future=False)
    if type(foreign_tables) == str:
        foreign_tables = [foreign_tables]
    mapping_schema_name = mapping_schema_name_generator(foreign_schema, foreign_server)
    upgrade_schema(schema_name= mapping_schema_name,db_uri= db_uri)
    create_foreign_table = f"""IMPORT FOREIGN SCHEMA {foreign_schema} LIMIT TO ({','.join(foreign_tables)})
    FROM SERVER {foreign_server} INTO {mapping_schema_name};"""
    if not foreign_tables:
        create_foreign_table = f"""IMPORT FOREIGN SCHEMA {foreign_schema}
        FROM SERVER {foreign_server} INTO {mapping_schema_name};"""
    legacy_engine.execute(text(create_foreign_table))


def downgrade_foreign_tables(table_name: Union[str, list[str]], foreign_schema: str,foreign_server: str = settings.POSTGRES_DB_RAW, db_uri:str=None):
    mapping_schema_name = mapping_schema_name_generator(foreign_schema, foreign_server)
    if db_uri:
        legacy_engine = create_engine(db_uri,future=False)
    if type(table_name) == str:
        table_names = [table_name]
    else:
        table_names = table_name
    for table_name in table_names:
        full_table_name = f"{mapping_schema_name}.{table_name}"
        drop_foreign_table = text(f"""DROP FOREIGN TABLE IF EXISTS {full_table_name};""")

        legacy_engine.execute(drop_foreign_table)


def insert_new_data_from_to_table_from_schema1_to_schema2(
    table_name: str, schema_from: str, schema_to: str
):
    table_from = f"{schema_from}.{table_name}"
    table_to = f"{schema_to}.{table_name}"
    stmt = text(
        f"""insert into {table_to} select table_from.* from {table_from} table_from 
				left join {table_to} table_to
				on table_from.id = table_to.id 
                where table_to.id is null;
    """
    )
    start_time = time.time()
    chapar_engine.execute(stmt)
    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == "__main__":
    schema_from = mapping_schema_name_generator(
        foreign_schema="public", foreign_server="datastore_server"
    )
    schema_to = "basic"
    table_name = "grid_calculation"
    # table_name = "grid_visualization"
    insert_new_data_from_to_table_from_schema1_to_schema2(
        table_name=table_name, schema_from=schema_from, schema_to=schema_to
    )
