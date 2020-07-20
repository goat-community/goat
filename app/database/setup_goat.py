#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from scripts import setup_db
from scripts import db_functions
import argparse
import sys
import os
from argparse import RawTextHelpFormatter
from scripts.db_functions import DB_connection
from scripts.db_functions import ReadYAML
from scripts.db_functions import restore_db
from scripts.db_functions import create_variable_container
from scripts.connect_to_spaces import download_raw_data, spaces_interaction

#Define command line options
help_text_type = '''Please define the setup type. 
             1. -t new_setup             Do a completely fresh setup and drop your old database.
             2. -t all                   Drop all tables created by GOAT and recreate them with new data (other tables will not be affected). 
             3. -t population            Update the population numbers.
             4. -t pois                  Update your POIs. 
             5. -t network               Update your network.
             6. -t functions             Update functions only.
             7. -t variable_container    Update variable container only.
             8. -t restore_dump          Restore a database dump that is labelled goat_db.sql
            '''

setup_types = ['new_setup','all','population','pois','network','functions','variable_container','restore_dump']

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('-t',help=help_text_type)
parser.add_argument('-n',help='Please define a namespace (e.g. muenchen) otherwise you can not restore the dump.')
parser.add_argument('-p',help='Please define if you would like to precalculate the heatmap automatically.',action='store_true')
parser.add_argument('-dr',help='Download raw data from DigitalOcean spaces. You need a spaces.yaml file for this.',action='store_true')

parser.add_argument('-db', help='Downloads a database dump from your Digital Ocean Spaces.',action="store_true")
parser.add_argument('-u', help='Upload a database dump to your Digital Ocean Spaces.',action="store_true")
parser.add_argument('-b', help='Backup your GOAT-Database.',action='store_true')


args = parser.parse_args()
setup_type = args.t
namespace = args.n


print('You decided to do the following setup-type: %s' % setup_type)

if args.dr == True and namespace != None:
    download_raw_data('goat', 'fra1','raw_data/'+namespace)

#if not setup_type or setup_type not in(setup_types):
#    sys.exit('You have defined no setup-type!')

if args.db == True or args.u == True or args.b == True:
    spaces_interaction(namespace,args)

if setup_type or setup_type in(setup_types):
    if (setup_type == 'functions'):
        ReadYAML().create_pgpass('',ReadYAML().db_credentials()[1])
        db_functions.update_functions()
    elif (setup_type == 'variable_container'):
        db_name,user,host,port,password = ReadYAML().db_credentials()[:5]
        create_variable_container(db_name,user,str(port),host,password)
    elif (setup_type == 'restore_dump' and namespace != None):
        restore_db(namespace)
    else:
        setup_db.setup_db(setup_type)

if (args.p  == True):
    os.system('python3 /opt/scripts/precalculate_heatmap.py')
