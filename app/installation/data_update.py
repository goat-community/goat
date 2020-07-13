#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os, glob, yaml
from pathlib import Path
import shapefile
import datetime

#Define command line options
parser = argparse.ArgumentParser()

help_text = '''You can define the update type.
             1. -t=network for updating the routing network.
             2. -t=thematic for updating the thematic data.
             3. -t=all for updating both 
            '''
parser.add_argument('-t', help=help_text)
update_type = parser.parse_args().t


if update_type is None:
    print('You have not selected any update type!')
else:
    print('You have selected type '+update_type+'!')
    
    #Take last timestamp
    file = open(str(Path.home())+"/app/data/"+"timestamps.txt","r")
    for line in file:
        pass
    timestamp=str(line.replace('\n',''))
    
    #Load credentials
    os.chdir(Path.home())
    with open(str(Path.home())+"/app/config/goat_config.yaml", 'r') as stream:
        config = yaml.load(stream)
       
    secrets = config["DATABASE"]
    host = secrets["HOST"]
    port = str(secrets["PORT"])
    db_name = secrets["DB_NAME"]
    user = secrets["USER"]
    password = secrets["PASSWORD"]
    
    os.chdir(str(Path.home())+'/app/data')
    
    #Define bounding box, the boundingbox is buffered by approx. 3 km
    bbox = shapefile.Reader("study_area.shp").bbox
    buffer = config['DATA_SOURCE']['BUFFER_BOUNDING_BOX']
    top = bbox[3]+buffer
    left = bbox[0]-buffer
    bottom = bbox[1]-buffer
    right = bbox[2]+buffer
    
    os.system('osmupdate study_area.osm %s study_area_update.osm -b=%f,%f,%f,%f' % (timestamp,left,bottom,right,top))
    #Add new timestamp
    currentDT = datetime.datetime.now()
    timestamp = currentDT.strftime("%Y-%m-%d")+'T'+currentDT.strftime("%H:%M:%S")+'Z'
    print(timestamp)
    file = open(str(Path.home())+"/app/data/"+"timestamps.txt","a")
    file.write(timestamp+'\n')
    file.close()
    
    if (update_type=='network' or update_type=='all'):
        os.system("PGPASSFILE=~/.pgpass psql -U %s -d %s -c 'DROP TABLE ways_userinput, ways_userinput_vertices_pgr;'" % (user,db_name))
        os.system('PGPASSFILE=~/.pgpass osm2pgrouting --dbname %s --host %s --username %s --file "study_area_update.osm" --conf ../config/mapconfig.xml --clean' % (db_name,host,user))
        os.system('PGPASSFILE=~/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,str(Path.home())+'/app/data_preparation/SQL/'+'network_preparation.sql'))
    
    #Update thematic data
    if (update_type=='thematic' or update_type=='all'):
        os.system("PGPASSFILE=~/.pgpass psql -U %s -d %s -c 'DROP TABLE planet_osm_point, planet_osm_line, planet_osm_polygon, planet_osm_roads'" % (user,db_name))
        os.system('PGPASSFILE=~/.pgpass osm2pgsql -d %s -H %s -U %s --hstore -E 4326 study_area_update.osm' % (db_name,host,user)) 
        
        os.chdir(str(Path.home())+'/app/data_preparation/SQL')
        os.system('PGPASSFILE=~/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'pois.sql'))
        source_population = config['DATA_SOURCE']['POPULATION']
        print ('It was chosen to use population from: ', source_population)
    
        if (source_population == 'extrapolation'):
            os.system('PGPASSFILE=~/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'buildings_residential.sql'))
            os.system('PGPASSFILE=~/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'census.sql'))
        elif(source_population == 'disaggregation'):
            os.system('PGPASSFILE=~/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'buildings_residential.sql'))
            os.system('PGPASSFILE=~/.pgpass psql -d %s -U %s -h %s -f %s' % (db_name,user,host,'population_disagregation.sql'))
    
