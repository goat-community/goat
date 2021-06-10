#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os 
os.environ['POSTGRES_DBNAME_TEMP'] = 'goattemp'
from db.db import Database
from psycopg2 import sql
import subprocess
import json 

from data_import import ReadYAML, CreateDatabase, DataImport, FileHelper
from data_preparation import PrepareDatabase, PrepareLayers


#Create temp database for setup and create connections
CreateDatabase(ReadYAML()).create_pgpass_files()
db_conn = Database()
#CreateDatabase(ReadYAML()).create_fresh_temp_db()

#Import custom data
data_import = DataImport(ReadYAML(),True,db_conn)
#data_import.import_data_folder('/opt/data/')

#Download OSM data
#data_import.prepare_planet_osm()

#Import OSM
#data_import.import_osm2pgsql()
#data_import.import_osm2pgrouting()

#Create variable container and function for data preparation
prepare_database = PrepareDatabase(ReadYAML(), True, db_conn)
prepare_database.data_preparation_table_types_functions()

#Prepare data layers
#prepare_layers = PrepareLayers(ReadYAML(), True, prepare_database, db_conn)
#prepare_layers.pois()
#prepare_layers.ways()

#prepare_layers.produce_population_points(ReadYAML().return_goat_conf()["DATA_REFINEMENT_VARIABLES"]["POPULATION"]) 
#prepare_layers.mapping_tables()
#prepare_layers.insert_osm_timestamp()

#Create database functions 
prepare_database.create_functions()
 
CreateDatabase(ReadYAML()).rename_databases()


os.environ['POSTGRES_DBNAME'] = 'goat'

