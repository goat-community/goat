# GOAT

## About

This is the experimental release of Geo Open Accessibility Tool (GOAT). GOAT is meant to be an open source, interactive, 
flexible and useful web-tool for accessibility planning. Its main data source is OpenStreetMap, however other data source can 
be used as well. The backbone of the application is a PostgreSQL/PostGIS database. 

## Software and Libraries used

The following software, languages and libraries are currently used:

PostgresSQL 10 
PostGIS 2.4
Pl/PgSQL
Geoserver 2.13.2
Python3
Shell
Openlayers 3
NodeJS 8.12.0
Nginx
Vagrant 2.1.2
Docker

## Setup GOAT

For the developed Vagrant and Docker are used. In order to start and customize GOAT for your study area you have to follow these steps:

1. Get a copy from GOAT

git clone https://github.com/EPajares/goat.git or copy as zip-folder

2. Install Virtualbox

https://www.virtualbox.org/

3. Install Vagrant

https://www.vagrantup.com/

4. Prepare shapefile and provide administrative boundaries

You need a shapefile with administrative boundaries and column with the number of inhabitants in this administrative 
unit, it works for any spatial resolution. The column has to be named “sum_pop” and has to be saved as string. 
As the population data is used for population disaggregation, data on higher resolution will give you a more 
accurate disaggregation.


