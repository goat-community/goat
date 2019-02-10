#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, glob, yaml
from pathlib import Path
import shapefile
os.system('sudo /etc/init.d/postgresql restart')
os.chdir(Path.home())
with open(str(Path.home())+"/app/config/goat_config.yaml", 'r') as stream:
    config = yaml.load(stream)
   
secrets = config["DATABASE"]
host = secrets["HOST"]
port = str(secrets["PORT"])
db_name = secrets["DB_NAME"]
user = secrets["USER"]
password = secrets["PASSWORD"]
os.system('echo '+':'.join([host,port,db_name,user,password])+' > .pgpass')
os.system("sudo chmod 600 .pgpass")

'''
os.system('sudo -u postgres psql -c "DROP DATABASE %s;"' % db_name) 
os.system('sudo -u postgres psql -c "DROP USER %s;"' % user) 
os.system('sudo -u postgres psql -c "CREATE DATABASE %s;"' % db_name)
os.system('sudo -u postgres psql -c "CREATE USER %s;"' % user)
os.system('sudo -u postgres psql -c "ALTER USER ' + user + ' WITH ENCRYPTED PASSWORD '+"'"+password+"'"+';"')
os.system('sudo -u postgres psql -c "ALTER USER %s WITH SUPERUSER;"' % user)
'''
#Create extensions
os.system('PGPASSFILE=~/.pgpass psql -d %s -U %s -h %s -c "CREATE EXTENSION postgis;CREATE EXTENSION pgrouting;CREATE EXTENSION hstore;CREATE EXTENSION plpython3u;"' % (db_name,user,host))
os.chdir('app/data')

#Define bounding box, the boundingbox is buffered by approx. 3 km
bbox = shapefile.Reader("study_area.shp").bbox
buffer = config['DATA_SOURCE']['BUFFER_BOUNDING_BOX']
top = bbox[3]+buffer
left = bbox[0]-buffer
bottom = bbox[1]-buffer
right = bbox[2]+buffer
'''
bounding_box = '--bounding-box top=%f left=%f bottom=%f right=%f' % (top,left,bottom,right)
 
os.system('wget --output-document="raw-osm.osm.pbf" %s' % config['DATA_SOURCE']['OSM_DOWNLOAD_LINK'])

os.system('osmosis --read-pbf file="raw-osm.osm.pbf" %s --write-xml file="study_area.osm"' % bounding_box)


os.system('osmconvert study_area.osm --drop-author --drop-version --out-osm -o=study_area_reduced.osm')
os.system('rm study_area | mv study_area_recuded.osm study_area.osm')
os.system('PGPASSFILE=~/.pgpass osm2pgsql -d %s -H %s -U %s --hstore -E 4326 study_area.osm' % (db_name,host,user)) 
os.system('PGPASSFILE=~/.pgpass osm2pgrouting --dbname %s --host %s --username %s --file "study_area.osm" --conf ../config/mapconfig.xml --clean' % (db_name,host,user))


for file in glob.glob("*.shp"):
    os.system('PGPASSFILE=~/.pgpass shp2pgsql -I -s 4326  %s public.%s | psql PGPASSWORD=%s -d %s -U %s -h %s -q' % (file,file.split('.')[0],password,db_name,user,host))
    print(file)

'''


os.chdir(str(Path.home())+'/app/data_preparation/SQL')

os.system('PGPASSFILE=~/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'create_tables.sql'))
os.system('PGPASSFILE=~/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'types.sql'))
os.system('PGPASSFILE=~/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'pois.sql'))
os.system('PGPASSFILE=~/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'network_preparation.sql'))

source_population = config['DATA_SOURCE']['POPULATION']
print ('It was chosen to use population from: ', source_population)
if (source_population == 'extrapolation'):
    os.system('PGPASSFILE=~/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'population_dissagregation.sql'))
    os.system('PGPASSFILE=~/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'census.sql'))
elif(source_population == 'disaggregation'):
    os.system('PGPASSFILE=~/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'population_dissagregation.sql'))

os.chdir(str(Path.home())+'/app/database_functions')
for file in glob.glob("*.sql"):
    os.system('PGPASSFILE=~/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,file))

