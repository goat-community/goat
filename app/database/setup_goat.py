#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, glob, yaml
from pathlib import Path
import shapefile
import datetime
from datetime import timedelta
import psycopg2
import argparse
from argparse import RawTextHelpFormatter
import sys

#Define command line options
help_text = '''You can define the update type. 
             1. -t new_setup                Do a completely fresh setup and drop your old database.
             2. -t update_all               Drop all tables created by GOAT and recreate them with new data (other tables will not be affected). 
             3. -t update_population        Update the population numbers.
             4. -t update_pois              Update your POIs. 
             5. -t update_network           Update your network.
            '''

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)


parser.add_argument('-t',help=help_text)
setup_type = parser.parse_args().t
print('You decided to the following setup-type: %s' % setup_type)

if not setup_type:
    sys.exit('You have defined no setup-type!')

#Read Configuration
with open("/opt/goat_config.yaml", 'r') as stream:
    config = yaml.load(stream,Loader=yaml.FullLoader)

pgpass = config["DATABASE"]
host = pgpass["HOST"]
port = str(pgpass["PORT"])
db_name = pgpass["DB_NAME"]+'new'
user = pgpass["USER"]
password = pgpass["PASSWORD"]
osm_data_recency = config['DATA_SOURCE']['OSM_DATA_RECENCY']


#Create pgpass-file for temporary database
os.system('echo '+':'.join([host,port,db_name,user,password])+' > /.pgpass')
os.system("chmod 600 .pgpass")
#Create temporary database
os.system('''psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='%s';"''' % db_name)
os.system('psql -U postgres -c "DROP DATABASE IF EXISTS %s;"' % db_name)
os.system('psql -U postgres -c "CREATE DATABASE %s;"' % db_name)
#Create extensions
os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -c "CREATE EXTENSION postgis;CREATE EXTENSION pgrouting;CREATE EXTENSION hstore;CREATE EXTENSION plpython3u;"' % (db_name,user,host))

os.chdir('/opt/data')


if (config['DATA_SOURCE']['OSM_DOWNLOAD_LINK'] != 'no_download' and setup_type == 'new_setup'):
     os.system('wget --no-check-certificate --output-document="raw-osm.osm.pbf" %s' % config['DATA_SOURCE']['OSM_DOWNLOAD_LINK'])

#Define bounding box, the boundingbox is buffered by approx. 3 km
bbox = shapefile.Reader("study_area.shp").bbox
buffer = config['DATA_SOURCE']['BUFFER_BOUNDING_BOX']
top = bbox[3]+buffer
left = bbox[0]-buffer
bottom = bbox[1]-buffer
right = bbox[2]+buffer

if (setup_type == 'new_setup'):

    bounding_box = '--bounding-box top=%f left=%f bottom=%f right=%f' % (top,left,bottom,right)
    os.system('osmosis --read-pbf file="raw-osm.osm.pbf" %s --write-xml file="study_area.osm"' % bounding_box)

    #Create timestamps
    os.system('rm timestamps.txt')
    os.system('touch timestamps.txt')
    #Create timestamp by substracting one day (usually Geofabrik files are one day old)
    currentDT = datetime.datetime.now()-timedelta(days=1)
    timestamp = currentDT.strftime("%Y-%m-%d")+'T'+currentDT.strftime("%H:%M:%S")+'Z'
    print(timestamp)
    file = open("timestamps.txt","a")
    file.write(timestamp+'\n')
    file.close()

    #Import shapefiles into database
    for file in glob.glob("*.shp"):
        print(file)
        os.system('PGPASSFILE=/.pgpass shp2pgsql -I -s 4326  %s public.%s | PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -q' % (file,file.split('.')[0],db_name,user,host))
        

#Use OSM-Update-Tool in order to fetch the most recent data
if (osm_data_recency == 'most_recent'):
    #Take last timestamp
    file = open('timestamps.txt','r')
    for line in file:
        pass
    timestamp=str(line.replace('\n',''))
    os.system('osmupdate study_area.osm %s study_area_update.osm -b=%f,%f,%f,%f' % (timestamp,left,bottom,right,top))

    #Add new timestamp
    currentDT = datetime.datetime.now()
    timestamp = currentDT.strftime("%Y-%m-%d")+'T'+currentDT.strftime("%H:%M:%S")+'Z'
    print(timestamp)
    file = open('timestamps.txt','a')
    file.write(timestamp+'\n')
    file.close()
    os.system('mv study_area_update.osm study_area.osm')

#Reduce files-size OSM-file
os.system('osmconvert study_area.osm --drop-author --drop-version --out-osm -o=study_area_reduced.osm')
os.system('rm study_area.osm | mv study_area_reduced.osm study_area.osm')

#Copy custom data into temporary database

if (setup_type in ['update_all','update_population','update_pois','update_network']):
    for file in glob.glob("*.shp"):
        table_name = file.split('.')[0]
        os.system('pg_dump -U %s -d %s -t %s | psql -d %s -U %s' % (user,pgpass["DB_NAME"],table_name,db_name,user))


#Create functions that are needed for data_preparation
os.chdir('/opt/data_preparation/SQL')
os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'create_tables.sql'))
os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'types.sql'))
os.chdir('/opt/database_functions/other')
os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'select_from_variable_container.sql'))
os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'split_long_way.sql'))

os.chdir('/opt/data')

if (setup_type in ['new_setup','update_all','update_population','update_pois','update_network']):
    os.system('PGPASSFILE=/.pgpass osm2pgsql -d %s -H %s -U %s --hstore -E 4326 study_area.osm' % (db_name,host,user)) 
    

if (setup_type in ['new_setup','update_population','update_pois']):    
    os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'../data_preparation/SQL/pois.sql'))
    if (setup_type in ['new_setup','update_population']):
        source_population = config['DATA_SOURCE']['POPULATION']
        print ('It was chosen to use population from: ', source_population)
        if (source_population == 'extrapolation'):
            os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'../data_preparation/SQL/buildings_residential.sql'))
            os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'../data_preparation/SQL/census.sql'))
        elif(source_population == 'disaggregation'):
            os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'../data_preparation/SQL/buildings_residential.sql'))
            os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'../data_preparation/SQL/population_disagregation.sql'))

if (setup_type in ['new_setup','update_all','update_network']):
    os.system('PGPASSFILE=/.pgpass osm2pgrouting --dbname %s --host %s --username %s --file "study_area.osm" --conf ../mapconfig.xml --clean' % (db_name,host,user))
    os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'../data_preparation/SQL/network_preparation.sql'))


if (setup_type == 'new_setup'):

    #Create pgpass for goat-database
    os.system('echo '+':'.join([host,port,pgpass["DB_NAME"],user,password])+' > /.pgpass')
    os.system("chmod 600 /.pgpass")

    for file in Path('../../database_functions/other').glob('*.sql'):
     os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,file))

    for file in Path('../../database_functions/routing').glob('*.sql'):
        os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,file))

    for file in Path('../../database_functions/heatmap').glob('*.sql'):
        os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,file))

    os.system('''psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='%s';"''' % pgpass["DB_NAME"])
    os.system('psql -U postgres -c "ALTER DATABASE %s RENAME TO %s;"' % (pgpass["DB_NAME"],pgpass["DB_NAME"]+'old'))
    os.system('psql -U postgres -c "ALTER DATABASE %s RENAME TO %s;"' % (db_name, pgpass["DB_NAME"]))

else:
    #Create pgpass for goat-database
    os.system('echo '+':'.join([host,port,pgpass["DB_NAME"],user,password])+' > /.pgpass')
    os.system("chmod 600 /.pgpass")

    con = psycopg2.connect("dbname='%s' user='%s' port = '%s' host='%s' password='%s'" % (
        db_name, user, port, host, password))
    cursor = con.cursor()
    #Select all tables that have changed
    sql_select_not_empty_tables = '''
    SELECT c.relname
    FROM pg_class c
    INNER JOIN pg_namespace n ON (n.oid = c.relnamespace)
    WHERE c.reltuples <> 0 AND c.relkind = 'r'
    AND nspname = 'public';
    '''
    cursor.execute(sql_select_not_empty_tables)
    tables_to_update = cursor.fetchall()
    #Refresh all tables that have changed
    for table in tables_to_update:  
        table = table[0]
        os.system('PGPASSFILE=/.pgpass psql -d %s -U %s -h %s -c "DROP TABLE %s CASCADE;"' % (pgpass["DB_NAME"],user,host,table))
        os.system('pg_dump -U %s -d %s -t %s | psql -d %s -U %s' % (user,db_name,table,pgpass["DB_NAME"],user))

    os.system('''psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='%s';"''' % db_name)
    os.system('psql -U postgres -c "DROP DATABASE %s;"' % db_name)

