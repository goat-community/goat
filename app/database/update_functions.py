#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, glob, yaml
from pathlib import Path

with open("/opt/goat_config.yaml", 'r') as stream:
    config = yaml.load(stream,Loader=yaml.FullLoader)

pgpass = config["DATABASE"]
host = pgpass["HOST"]
port = str(pgpass["PORT"])
db_name = pgpass["DB_NAME"]
user = pgpass["USER"]
password = pgpass["PASSWORD"]

os.chdir('/opt')
os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'data_preparation/SQL/types.sql'))

for file in Path('database_functions/other').glob('*.sql'):
     os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,file))

for file in Path('database_functions/routing').glob('*.sql'):
     os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,file))

for file in Path('database_functions/heatmap').glob('*.sql'):
     os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,file))
