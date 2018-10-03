#!/bin/sh
#Variables
source ~/app/config/secrets.js

echo "$HOST:$PORT:$DATABASE:$USER:$PASSWORD" > .pgpass
chmod 600 .pgpass

sudo -u postgres psql -c "drop database goat"
sudo -u postgres psql -c "drop user goat;"
sudo -u postgres psql -c "create database goat;"
sudo -u postgres psql -c "create user goat;"
sudo -u postgres psql -c "alter user goat with encrypted password 'earlmanigault';"
sudo -u postgres psql -c "ALTER USER goat with superuser;"


PGPASSFILE=~/.pgpass psql -d $DATABASE -U $USER -h $HOST -c "create extension postgis;"
PGPASSFILE=~/.pgpass psql -d $DATABASE -U $USER -h $HOST -c "create extension pgrouting;"
PGPASSFILE=~/.pgpass psql -d $DATABASE -U $USER -h $HOST -c "create extension hstore;"


cd ~/app/data
wget --output-document="raw-osm.osm.pbf" $DOWNLOAD_LINK

osmosis --read-pbf file="raw-osm.osm.pbf" $BOUNDING_BOX --write-xml file="study_area.osm"

PGPASSFILE=~/.pgpass osm2pgsql -d $DATABASE -H $HOST -U $USER --hstore -E 4326 study_area.osm 
PGPASSFILE=~/.pgpass osm2pgrouting --dbname $DATABASE --host $HOST --username $USER --file "study_area.osm" --conf ../config/mapconfig.xml --clean
PGPASSFILE=~/.pgpass shp2pgsql -I -s 4326  study_area.shp public.study_area | psql PGPASSWORD=PASSWORD -d $DATABASE -U $USER -h $HOST -q

#Schreibtisch has to be replaced by GitHub Link

for file in ../data_preparation/SQL/*; do PGPASSFILE=~/.pgpass psql -d $DATABASE -U $USER -h $HOST -f $file 2>/dev/null; done
:

for file in ../database_functions/*; do PGPASSFILE=~/.pgpass psql -d $DATABASE -U $USER -h $HOST -f $file 2>/dev/null; done
: 

#python3 ../data_preparation/Python/precalculate_grid_thematic.py



