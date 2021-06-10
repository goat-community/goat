import os 
os.environ['POSTGRES_DBNAME_TEMP'] = 'goattemp'
from db.db import Database
from psycopg2 import sql
import subprocess
import json 

from data_import import ReadYAML, CreateDatabase, DataImport, FileHelper
from data_preparation import PrepareDatabase, Population 


db_conn = Database()


ReadYAML().create_pgpass('','goat')
ReadYAML().create_pgpass('temp','goat')


#CreateDatabase(db_conf).create_fresh_temp_db()


#cls_import.import_osm2pgrouting()
#cls_import.prepare_planet_osm()
#cls_import.import_osm2pgsql()


#PrepareDatabase(db_conf,goat_conf,True).create_variable_container()
#PrepareDatabase(db_conf,goat_conf,True).update_functions()
#PrepareDatabase(db_conf,goat_conf,True).data_preparation_table_types_functions()

cls_import = DataImport(ReadYAML(),True,db_conn)
prepare_db = PrepareDatabase(ReadYAML(),True,db_conn)

#PrepareDatabase(db_conf,goat_conf,True).execute_script_psql('/opt/data_preparation/SQL/create_tables.sql')

Population(ReadYAML(),prepare_db,True).prepare_data(cls_import, FileHelper())
Population(ReadYAML(),prepare_db,True).produce_population_points('census_extrapolation')


os.environ['POSTGRES_DBNAME'] = 'goat'


