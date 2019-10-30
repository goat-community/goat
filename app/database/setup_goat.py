#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, glob, yaml
from pathlib import Path
import shapefile
import datetime


with open("/opt/goat_config.yaml", 'r') as stream:
    config = yaml.load(stream)

pgpass = config["DATABASE"]
host = pgpass["HOST"]
port = str(pgpass["PORT"])
db_name = pgpass["DB_NAME"]+'new'
user = pgpass["USER"]
password = pgpass["PASSWORD"]

os.system('echo '+':'.join([host,port,db_name,user,password])+' > /.pgpass')
os.system("chmod 600 .pgpass")

os.system('psql -U postgres -c "CREATE DATABASE %s;"' % db_name)

# #Create extensions
os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -c "CREATE EXTENSION postgis;CREATE EXTENSION pgrouting;CREATE EXTENSION hstore;CREATE EXTENSION plpython3u;"' % (db_name,user,host))

os.chdir('/opt/data')

#Define bounding box, the boundingbox is buffered by approx. 3 km
bbox = shapefile.Reader("study_area.shp").bbox
buffer = config['DATA_SOURCE']['BUFFER_BOUNDING_BOX']
top = bbox[3]+buffer
left = bbox[0]-buffer
bottom = bbox[1]-buffer
right = bbox[2]+buffer

bounding_box = '--bounding-box top=%f left=%f bottom=%f right=%f' % (top,left,bottom,right)

if (config['DATA_SOURCE']['OSM_DOWNLOAD_LINK'] != 'no_download'):
     os.system('wget --no-check-certificate --output-document="raw-osm.osm.pbf" %s' % config['DATA_SOURCE']['OSM_DOWNLOAD_LINK'])

os.system('osmosis --read-pbf file="raw-osm.osm.pbf" %s --write-xml file="study_area.osm"' % bounding_box)

#Create timestamps
os.system('rm timestamps.txt')
os.system('touch timestamps.txt')
currentDT = datetime.datetime.now()
timestamp = currentDT.strftime("%Y-%m-%d")+'T'+currentDT.strftime("%H:%M:%S")+'Z'
print(timestamp)
file = open("timestamps.txt","a")
file.write(timestamp+'\n')
file.close()

os.system('osmconvert study_area.osm --drop-author --drop-version --out-osm -o=study_area_reduced.osm')
os.system('rm study_area.osm | mv study_area_reduced.osm study_area.osm')
os.system('PGPASSFILE=/.pgpass osm2pgsql -d %s -H %s -U %s --hstore -E 4326 study_area.osm' % (db_name,host,user)) 
os.system('PGPASSFILE=/.pgpass osm2pgrouting --dbname %s --host %s --username %s --file "study_area.osm" --conf ../mapconfig.xml --clean' % (db_name,host,user))


for file in glob.glob("*.shp"):
     print(file)
     os.system('PGPASSFILE=/.pgpass shp2pgsql -I -s 4326  %s public.%s | PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -q' % (file,file.split('.')[0],db_name,user,host))
     

os.chdir('../data_preparation/SQL')

os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'create_tables.sql'))
os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'types.sql'))
os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'pois.sql'))

os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'../../database_functions/other/select_from_variable_container.sql'))
os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'../../database_functions/other/split_long_way.sql'))
os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'network_preparation.sql'))

source_population = config['DATA_SOURCE']['POPULATION']
print ('It was chosen to use population from: ', source_population)
if (source_population == 'extrapolation'):
    os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'buildings_residential.sql'))
    os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'census.sql'))
elif(source_population == 'disaggregation'):
    os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'buildings_residential.sql'))
    os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'population_disagregation.sql'))


for file in Path('../../database_functions/other').glob('*.sql'):
     os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,file))

for file in Path('../../database_functions/routing').glob('*.sql'):
     os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,file))

for file in Path('../../database_functions/heatmap').glob('*.sql'):
     os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,file))


os.system('''psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='%s';"''' % pgpass["DB_NAME"])
os.system('psql -U postgres -c "ALTER DATABASE %s RENAME TO %s;"' % (pgpass["DB_NAME"],pgpass["DB_NAME"]+'old'))
os.system('psql -U postgres -c "ALTER DATABASE %s RENAME TO %s;"' % (db_name, pgpass["DB_NAME"]))
os.system('psql -U postgres -c "DROP DATABASE %s;"' % (pgpass["DB_NAME"]+'old'))
