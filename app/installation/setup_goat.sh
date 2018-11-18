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
PGPASSFILE=~/.pgpass psql -d $DATABASE -U $USER -h $HOST -c "create extension plpython3u;"
cd ~/app/data
wget --output-document="raw-osm.osm.pbf" $DOWNLOAD_LINK

if [ -z "$BOUNDING_BOX_2" ]
then 
    echo 'One bounding box was chosen.'
    osmosis --read-pbf file="raw-osm.osm.pbf" $BOUNDING_BOX --write-xml file="study_area.osm"
else
    echo 'You have set two bounding boxes. The raw-file will be cut and then merged together'
    osmosis --read-pbf file="raw-osm.osm.pbf" $BOUNDING_BOX --write-xml file="study_area1.osm"
    osmosis --read-pbf file="raw-osm.osm.pbf" $BOUNDING_BOX_2 --write-xml file="study_area2.osm"
    osmosis --rx study_area1.osm --rx study_area2.osm --m --wx study_area.osm
fi

PGPASSFILE=~/.pgpass osm2pgsql -d $DATABASE -H $HOST -U $USER --hstore -E 4326 study_area.osm 
PGPASSFILE=~/.pgpass osm2pgrouting --dbname $DATABASE --host $HOST --username $USER --file "study_area.osm" --conf ../config/mapconfig.xml --clean
PGPASSFILE=~/.pgpass shp2pgsql -I -s 4326  study_area.shp public.study_area | psql PGPASSWORD=PASSWORD -d $DATABASE -U $USER -h $HOST -q



if [ -e population.shp ]
then
    echo 'Your custom population table will be used.'
    PGPASSFILE=~/.pgpass shp2pgsql -I -s 4326  population.shp public.population | psql PGPASSWORD=PASSWORD -d $DATABASE -U $USER -h $HOST -q
else
    echo 'The population will be disaggregated.'
    if [ -e landuse.shp ]
    then
        echo 'Your custom landuse table will be used.'
        PGPASSFILE=~/.pgpass shp2pgsql -I -s 4326  landuse.shp public.landuse | psql PGPASSWORD=PASSWORD -d $DATABASE -U $USER -h $HOST -q
    else
        echo 'For the population disaggregation only landuse from OSM will be used.'
    fi
fi

for file in ../data_preparation/SQL/*; do PGPASSFILE=~/.pgpass psql -d $DATABASE -U $USER -h $HOST -f $file 2>/dev/null; done
:

for file in ../database_functions/*; do PGPASSFILE=~/.pgpass psql -d $DATABASE -U $USER -h $HOST -f $file 2>/dev/null; done
: 



