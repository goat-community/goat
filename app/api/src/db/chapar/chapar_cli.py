#!/usr/bin/env python
import os
import subprocess

import click
import inquirer
import sqlalchemy_utils as sqlutils
from alembic_utils.pg_extension import PGExtension
from engines import chapar_engine, chapar_uri
from rich.console import Console
from rich.table import Table
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker

from alembic import command
from alembic.config import Config
from src.core.config import SyncPostgresDsn, settings
from src.db.chapar import init_remote_table as remote_table
from src.db.chapar.init_remote_table import upgrade_foreign_server, upgrade_mapping_user
from src.db.chapar.projects import projects
from src.db.models import StudyArea
from src.db.session import legacy_engine

DUMP_FILE_NAME = 'staging_schema_backup.tar'
CHAPAR_DBNAME = 'chapar'
STAGING_DBNAME = 'staging'
GEONODE_DBNAME = 'geonode_data'

@click.group()
def cli():
    pass


def run_migrations(script_location: str='./', dsn: str=None) -> None:
    alembic_cfg = Config(file_='alembic.ini')
    alembic_cfg.set_main_option('script_location', script_location)
    alembic_cfg.set_main_option('sqlalchemy.url', dsn)
    command.upgrade(alembic_cfg, 'head')


def list_foreign_servers():
    q = text('''
        select 
            srvname as name, 
            srvowner::regrole as owner, 
            fdwname as wrapper, 
            srvoptions as options
        from pg_foreign_server
        join pg_foreign_data_wrapper w on w.oid = srvfdw;
        ''')
    response = legacy_engine.execute(q)
    cols = response._metadata.keys
    servers = []
    rows_ = []
    for row in response:
        servers.append(list(row))
    return cols, servers

def print_foreign_servers():
    cols, servers = list_foreign_servers()
    rows = []
    for row in servers:
        row = [str(col) for col in row]
        rows.append(row)
        

    table = Table(title="Foreign servers")
    for col in cols:
        table.add_column(col)
    for row in rows:
        table.add_row(*row)

    console = Console()
    console.print(table)
    

@click.command()
@click.option('--server_name',prompt="Enter a name for server")
@click.option('--host',prompt='Enter HOST name')
@click.option('--port',prompt='Eneter PORT number')
@click.option('--dbname',prompt='Enter Database Name')
def add_server(server_name,host,port,dbname):
    upgrade_foreign_server(foreign_server=server_name,
                           host=str(host),
                           port=str(port),
                           dbname=dbname)
    print_foreign_servers()
    

@click.command()
@click.option('--server_name')
@click.option('--server_user')
@click.option('--server_user_password')
def add_mapping_user(server_name=None,server_user=None,server_user_password=None):
    if not server_name:
        cols, servers = list_foreign_servers()
        server_names = [server[0] for server in servers]
        server_name = inquirer.list_input("Select server to add mapping user:", choices=server_names)
    server_user = server_user or click.prompt("Enter server's user name")
    server_user_password = server_user_password or click.prompt(f"Enter password for {server_user}", hide_input=True)
    upgrade_mapping_user(foreign_server=server_name,server_user=server_user,password=server_user_password)
    print("Mapping user added!")


@click.command()
@click.option('--project')
@click.option('--project_name',prompt='Enter a name for the staging project')
def backup_staging_database(project=None, project_name=None):
    if not project:
        projects_ = projects.keys()
        project = inquirer.list_input("Select project to make backup:", choices=projects_)
    
    table_args = ' '.join(['-t ' + table for table in projects[project]['tables']])
    directory_path = f"/tmp/chapar/staging_backups"
    try:
        os.makedirs(directory_path)
    except FileExistsError:
        pass
    file_path = f"{directory_path}/{project_name}.backup"
    dump_command = f'PGPASSWORD="{settings.POSTGRES_PASSWORD}" pg_dump --verbose --file={file_path} --format=c --host={settings.POSTGRES_SERVER} --port=5432 --username={settings.POSTGRES_USER} {table_args} {settings.POSTGRES_DB}'
    subprocess.run(dump_command)

def get_db_uri(dbname):
    return SyncPostgresDsn.build(
            scheme="postgresql",
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_SERVER,
            path=f"/{dbname}",
        )


def duplicate_server_with_template(dbname=CHAPAR_DBNAME):
    query = text(f'''
                SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity 
                WHERE pg_stat_activity.datname = '{settings.POSTGRES_DB}' AND pid <> pg_backend_pid();
                CREATE DATABASE {dbname} WITH TEMPLATE {settings.POSTGRES_DB} OWNER {settings.POSTGRES_USER};
                 ''')
    terminate_users_query = text(f'''
                SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity 
                WHERE pg_stat_activity.datname = '{settings.POSTGRES_DB}' AND pid <> pg_backend_pid();
                                 ''')
    duplicate_server_query = text(f'''
                CREATE DATABASE {dbname} WITH TEMPLATE {settings.POSTGRES_DB} OWNER {settings.POSTGRES_USER};
                                  ''')
    session = sessionmaker(bind=legacy_engine)()
    session.connection().connection.set_isolation_level(0)
    session.execute(terminate_users_query)
    session.execute(duplicate_server_query)
    session.connection().connection.set_isolation_level(1)


def dump_schema():
    dump_address = f'/tmp/{DUMP_FILE_NAME}'
    dump_schema_command = f'PGPASSWORD="{settings.POSTGRES_PASSWORD}" pg_dump -d {settings.POSTGRES_DB} -U {settings.POSTGRES_USER} -h {settings.POSTGRES_SERVER} -F t -s -x > {dump_address}'
    os.system(dump_schema_command)
    print(f'Dump created at {dump_address}')
    return dump_address

def restore_schema():
    dump_address = f'/tmp/{DUMP_FILE_NAME}'
    restore_schema_command = f'PGPASSWORD="{settings.POSTGRES_PASSWORD}" pg_restore -d {CHAPAR_DBNAME} -U {settings.POSTGRES_USER} -h {settings.POSTGRES_SERVER} -v {dump_address}'
    os.system(restore_schema_command)
    print(f'Dump successfully restored!')
    return 0

@click.command()
@click.option('--dbname',prompt='Enter dbname')
def drop_database(dbname):
    db_uri = get_db_uri(dbname)
    if not sqlutils.database_exists(db_uri):
        print(f'Database {dbname} does not exist!')
    else:
        sqlutils.drop_database(db_uri)
        print(f'Database{dbname} successfully dropped!')


def create_database(dbname):
    db_uri =  db_uri = get_db_uri(dbname)
    if not sqlutils.database_exists(db_uri):
        sqlutils.create_database(db_uri)
        print(f'Database {dbname} successfully created.')
    else:
        print(f'Database {dbname} already exists. skip.')

def create_staging_database():
    duplicate_server_with_template(dbname=STAGING_DBNAME)

def create_chapar_database(dbname=CHAPAR_DBNAME):
    db_uri = get_db_uri(dbname)
    if not sqlutils.database_exists(db_uri):
        
        sqlutils.create_database(db_uri)
        print(f'Database {dbname} created!')
        dump_schema()
        print(f'schema successfully dumped')
        restore_schema()
        print(f'schema successfully restored.')
    else:
        print(f'Database {dbname} already exists!')


def create_chapar_database_alembic(dbname=CHAPAR_DBNAME):
    db_uri = get_db_uri(dbname)
    if not sqlutils.database_exists(db_uri):
        sqlutils.create_database(db_uri)
        
    else:
        print(f'Database {dbname} already exists!')
    
    run_migrations(script_location='/app/alembic',dsn=db_uri)

def enable_postgis(db_uri):
    postgis_extensions = [
        'postgis',
        'postgis_raster',
        'postgis_topology',
        'postgis_sfcgal',
        'fuzzystrmatch',
        'address_standardizer',
        'address_standardizer_data_us',
        'postgis_tiger_geocoder'
    ]
    for extension in postgis_extensions:
        remote_table.upgrade_extension(extension,db_uri)
        
    

def create_chapar_database():
    create_database('chapar')
    dump_schema()
    restore_schema()

def create_foreign_server(dbname:str):
    remote_table.upgrade_postgres_fdw(db_uri=chapar_uri)
    remote_table.upgrade_foreign_server(dbname=dbname, host=settings.POSTGRES_SERVER, port=5432)
    remote_table.upgrade_mapping_user(db_uri=chapar_uri, foreign_server=dbname, server_user=settings.POSTGRES_USER, password=settings.POSTGRES_PASSWORD)

def create_foreign_tables_for_staging():
    remote_table.upgrade_foreign_tables(
        foreign_schema='basic',
        foreign_server=STAGING_DBNAME,
        db_uri=get_db_uri('chapar')
    )
    remote_table.upgrade_foreign_tables(
        foreign_schema='customer',
        foreign_server=STAGING_DBNAME,
        db_uri=get_db_uri('chapar')
    )

def create_foreign_tables_for_project(project_name:str):
    remote_table.upgrade_foreign_tables(
        foreign_tables=projects[project_name]['tables'],
        foreign_schema=projects[project_name]['raw_db_schema'],
        db_uri=get_db_uri('chapar')
    )

def remove_foreign_tables(project_name:str):
    remote_table.downgrade_foreign_tables(
        table_name=projects[project_name]['tables'],
        foreign_schema=projects[project_name]['raw_db_schema'],
        db_uri=get_db_uri('chapar')
    )

def reset_foreign_tables(project_name:str):
    remove_foreign_tables(project_name)
    create_foreign_tables_for_project(project_name)


def get_last_study_area_id():
    query = select(StudyArea.id).order_by(StudyArea.id.desc())
    study_area = chapar_engine.execute(query).first()
    return study_area.id

def import_study_area(foreign_server:str, foreign_schema:str, study_area_id:int):
    staging_schema_name=remote_table.mapping_schema_name_generator('basic', STAGING_DBNAME)
    geonode_schema_name = remote_table.mapping_schema_name_generator('public', settings.POSTGRES_DB_RAW)
    query = text(f'''
                INSERT INTO {staging_schema_name}.study_area   (id,
                                                name,
                                                geom,
                                                population,
                                                setting,
                                                buffer_geom_heatmap)
                SELECT  id,
                        name,
                        geom,
                        population,
                        setting,
                        buffer_geom_heatmap
                FROM {geonode_schema_name}.study_area s
                WHERE s.id = {study_area_id}
                 ''')
    chapar_engine.execute(query)


    

def import_sub_study_area(foreign_server:str, foreign_schema:str, study_area_id:int):
    foreign_schema_name = remote_table.mapping_schema_name_generator(foreign_schema, foreign_server)
    query = text(f'''
                    INSERT INTO basic.sub_study_area (
                        name,
                        default_building_levels,
                        default_roof_levels,
                        area,
                        geom,
                        population,
                        study_area_id
                    )
                    SELECT
                            s.name,
                            s.default_building_levels,
                            s.default_roof_levels,
                            s.area,
                            s.geom,
                            s.population,
                            s.study_area_id
                    FROM {foreign_schema_name}.sub_study_area s
                    WHERE s.study_area_id = {study_area_id}
                 ''')
    chapar_engine.execute(query)

def import_grid_visualization(foreign_server:str, foreign_schema:str, study_area_id:int):
    foreign_schema_name = remote_table.mapping_schema_name_generator(foreign_schema, foreign_server)
    query = text(f'''
                    INSERT INTO basic.grid_visualization (  id,
                                                            geom,
                                                            area_isochrone,
                                                            percentile_area_isochrone,
                                                            percentile_population,
                                                            population)
                    SELECT  g.id,
                            g.geom,
                            g.area_isochrone,
                            g.percentile_area_isochrone,
                            g.percentile_population,
                            g.population
                    FROM
                    (
                        SELECT  id,
                                geom,
                                area_isochrone,
                                percentile_area_isochrone,
                                percentile_population,
                                population
                        {foreign_schema_name}.grid_visualization g1, {foreign_schema_name}.study_area s 
                        WHERE ST_Intersects(ST_Centroid(g1.geom), s.geom)
                        AND g1.geom && s.geom 
                    )  g1 
                    LEFT JOIN basic.grid_visualiation g2
                    ON g1.id = g2.id
                    WHERE g2.id IS NULL
                 ''')
    chapar_engine.execute(query)

def import_grid_calculations(foreign_server:str, foreign_schema:str, study_area_id:int):
    foreign_schema_name = remote_table.mapping_schema_name_generator(foreign_schema, foreign_server)
    query = text(f'''
                    WITH new_grid_cs as 
                    (
                        SELECT gc.*
                        FROM {foreign_schema_name}.grid_calculation gc,
                        basic.grid_visualization gv 
                        WHERE gv.id = gc.grid_visualization_id 
                    )
                    SELECT new_grid_cs.*
                    FROM new_grid_cs
                    LEFT JOIN basic.grid_calculation p
                    ON new_grid_cs.id = p.id 
                    WHERE p.id IS NULL
                 ''')
    chapar_engine.execute(query)


def prepare_dbs():
    # 1. Duplicate main database as STAGING
    # create_staging_database()
    # 2. Duplicate main database structure as CHAPAR
    create_chapar_database()
    # 3. Create foregin server to STAGING in CHAPAR
    create_foreign_server(dbname=STAGING_DBNAME)
    # 4. Import foreign tables for STAGING in CHAPAR
    create_foreign_tables_for_staging()
    # 5. Create foreign server to Geonode in CHAPAR
    remote_table.upgrade_foreign_server(dbname=settings.POSTGRES_DB_RAW, host=settings.POSTGRES_SERVER_RAW, port=settings.POSTGRES_OUTER_PORT_RAW)
    remote_table.upgrade_mapping_user(db_uri=chapar_uri, foreign_server=settings.POSTGRES_DB_RAW, server_user=settings.POSTGRES_USER_RAW, password=settings.POSTGRES_PASSWORD_RAW)
    


if __name__ == '__main__':
    
    # drop_database()
    prepare_dbs()
    # create_foreign_server(dbname=GEONODE_DBNAME)
    create_foreign_tables_for_project('green')
    # import_sub_study_area(
    #     db_uri=get_db_uri('chapar'),
    #     foreign_server=settings.POSTGRES_DB_RAW,
    #     foreign_schema='public',
    #     foreign_study_area_id=9376
    # )
    # reset_foreign_tables('green')
    # import_study_area(
    #     db_uri=get_db_uri('chapar'),
    #     foreign_server=settings.POSTGRES_DB_RAW,
    #     foreign_schema='public',
    #     study_area_id=9376
    # )
    pass