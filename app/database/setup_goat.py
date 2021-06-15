#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse, sys, os
from argparse import RawTextHelpFormatter
from scripts.connect_to_spaces import download_raw_data, spaces_interaction
from scripts.db.db import Database
from scripts.data_import import ReadYAML, CreateDatabase, DataImport, FileHelper
from scripts.data_preparation import PrepareDatabase, PrepareLayers

class GoatSetup():
    def fresh_setup(self):
        #Create temp database for setup and create connections
        CreateDatabase(ReadYAML()).create_pgpass_files()
        db_conn = Database('temp')

        CreateDatabase(ReadYAML()).create_fresh_temp_db()

        #Import custom data
        data_import = DataImport(ReadYAML(),True,db_conn)
        data_import.import_data_folder('/opt/data/')

        #Download OSM data
        data_import.prepare_planet_osm()

        #Import OSM
        data_import.import_osm2pgsql()
        data_import.import_osm2pgrouting()

        #Create variable container and function for data preparation
        prepare_database = PrepareDatabase(ReadYAML(), True, db_conn)
        prepare_database.data_preparation_table_types_functions()

        #Prepare data layers
        prepare_layers = PrepareLayers(ReadYAML(), True, prepare_database, db_conn)
        prepare_layers.pois()
        prepare_layers.ways()

        prepare_layers.produce_population_points(ReadYAML().return_goat_conf()["DATA_REFINEMENT_VARIABLES"]["POPULATION"]) 
        prepare_layers.mapping_tables()
        prepare_layers.insert_osm_timestamp()

        #Create database functions and rename database
        prepare_database.create_functions()
        CreateDatabase(ReadYAML()).rename_databases()



CreateDatabase(ReadYAML()).create_pgpass_files()
db_conn = Database()
data_import = DataImport(ReadYAML(), False, db_conn)
prepare_database = PrepareDatabase(ReadYAML(), False, db_conn)



#Define command line options
help_text_type = '''Please define the setup type. 
             1. -t new_setup             Do a completely fresh setup and drop your old database.
             2. -t functions             Update functions only.
             3. -t variable_container    Update variable container only.
             4. -t restore_dump          Restore a database dump. To be used in combination with -n or -f.
            '''

setup_types = ['new_setup','functions','variable_container','restore_dump']

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('-t',help=help_text_type)
parser.add_argument('-n',help='Please define a namespace (e.g. muenchen) for managing dumps with namespace.')
parser.add_argument('-p',help='Please define if you would like to precalculate the heatmap automatically.',action='store_true')
parser.add_argument('-dr',help='Download raw data from DigitalOcean spaces. You need a spaces.yaml file for this.',action='store_true')
parser.add_argument('-db', help='Downloads a database dump from your Digital Ocean Spaces.',action="store_true")
parser.add_argument('-u', help='Upload a database dump to your Digital Ocean Spaces.',action="store_true")
parser.add_argument('-b', help='Backup your GOAT-Database.',action='store_true')
parser.add_argument('-f', help='Please provide the full path to a database dump (e.g. /opt/backups/neuperlach_dump2021-06-13.sql).')
args = parser.parse_args()
setup_type = args.t
namespace = args.n

print('You decided to do the following setup-type: %s' % setup_type)

if args.dr == True and namespace != None:
    download_raw_data('goat', 'fra1','raw_data/'+namespace)

#if not setup_type or setup_type not in(setup_types):
#    sys.exit('You have defined no setup-type!')

if args.db == True or args.u == True or args.b == True:
    backup_location = spaces_interaction(namespace,args)


if setup_type or setup_type in(setup_types):
    if (setup_type == 'functions'):
        prepare_database.create_functions()
    elif (setup_type == 'variable_container'):
        prepare_database.create_variable_container()
    elif (setup_type == 'restore_dump' and namespace != None):
        backup_location = data_import.find_newest_dump(namespace)
        print('###############################Following dump will be restored: %s###################################' % backup_location)
        data_import.restore_db(backup_location)
    elif (setup_type == 'restore_dump' and args.f != None):
        data_import.restore_db(args.f)
    elif setup_type == 'new_setup':
        GoatSetup().fresh_setup()
    else:
        print('Error: Please specify a valid setup type.')

if (args.p  == True):
    os.system('python3 /opt/scripts/precalculate_heatmap.py')
