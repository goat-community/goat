#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from scripts import setup_db
from scripts import db_functions
import argparse
import sys
from argparse import RawTextHelpFormatter

#Define command line options
help_text = '''You can define the update type. 
             1. -t new_setup             Do a completely fresh setup and drop your old database.
             2. -t all                   Drop all tables created by GOAT and recreate them with new data (other tables will not be affected). 
             3. -t population            Update the population numbers.
             4. -t pois                  Update your POIs. 
             5. -t network               Update your network.
             6. -t functions             Update functions only.
             7. -t variable_container    Update variable container only.
            '''

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)


parser.add_argument('-t',help=help_text)
setup_type = parser.parse_args().t
print('You decided to do the following setup-type: %s' % setup_type)

if not setup_type:
    sys.exit('You have defined no setup-type!')
elif (setup_type == 'functions'):
    db_functions.update_functions()
elif (setup_type == 'variable_container'):
    sql_command = db_functions.create_variable_container()
    db_functions.update_variable_container(sql_command)
else:
    setup_db.setup_db(setup_type)
