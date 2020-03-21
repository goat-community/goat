#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from scripts import setup_db
from scripts import db_functions
import argparse
import sys
from argparse import RawTextHelpFormatter
from scripts.db_functions import DB_connection
from scripts.db_functions import ReadYAML
from scripts.db_functions import restore_db
from scripts.db_functions import create_variable_container
#Define command line options
help_text_type = '''You can define the update type. 
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
parser.add_argument('-n',help='Please define a namespace (e.g. muenchen) otherwise no backup can be done.')

setup_type = parser.parse_args().t
namespace = parser.parse_args().n
print('You decided to do the following setup-type: %s' % setup_type)


if not setup_type or setup_type not in(setup_types):
    sys.exit('You have defined no setup-type!')
elif (setup_type == 'functions'):
    ReadYAML().create_pgpass('')
    db_functions.update_functions()
elif (setup_type == 'variable_container'):
    ReadYAML().create_pgpass('')
    db_name,user,host,port,password = ReadYAML().db_credentials()
    create_variable_container(db_name,user,str(port),host,password)
elif (setup_type == 'restore_dump' and namespace != None):
    restore_db(namespace)
else:
    setup_db.setup_db(setup_type)


