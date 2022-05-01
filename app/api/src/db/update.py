import argparse
import sys
from argparse import RawTextHelpFormatter
from src.db.seed_data import DataUpdate
from src.utils import print_info, print_warning
from src.db.session import sync_session

help_text_type = '''Define the table groups that should be updated as a comma-seperated list. Available categories are:
    Layers:
    - aoi    
    - poi

    Configs:
    - opportunity_config
    - layer_config
    - customization

    All:
    - all
 '''

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-t', help=help_text_type)

args = parser.parse_args()
if args is None:
    sys.exit()
    print_warning("No were arguments provided.")

try: 
    table_groups = args.t.split(',')
except:
    print_warning("Table arguments are provided not correctly as comma-seperated list.")
    sys.exit()

db = sync_session()
data_update = DataUpdate(db)

data_update.connect_fdw()
data_update.update_table_groups(db, table_groups)




