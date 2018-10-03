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

#### 1. Get a copy from GOAT

`git clone https://github.com/EPajares/goat.git` 
or copy as zip-folder

#### 2. Install Virtualbox

https://www.virtualbox.org/

#### 3. Install Vagrant

https://www.vagrantup.com/

#### 4. Prepare shapefile and provide administrative boundaries

You need a shapefile with administrative boundaries and column with the number of inhabitants in this administrative 
unit, it works for any spatial resolution. The column has to be named “sum_pop” and has to be saved as string. 
As the population data is used for population disaggregation, data on higher resolution will give you a more 
accurate disaggregation.

**You have to put the file into the app/data folder.**

#### 5. Define your bounding box and the OSM-Downloadlink

Open the file customize the DOWNLOAD_LINK and BOUNDING_BOX.

#### 6. Setup GOAT

##### 6.1. Start Vagrant

Open a command window and go into the project folder. Run the command:

`vagrant up`

For more Vagrant commands checkout:

https://gist.github.com/wpscholar/a49594e2e2b918f4d0c4

##### 6.2. Fill your database

`vagrant ssh`

`sudo bash app/installation/setup_goat.sh`

##### Update data

In case you want to update all your data you can simply run the following from your project directory.

`sudo /etc/init.d/postgresql restart`
`sudo bash app/installation/setup_goat.sh`

Note this will drop your database and create a new database. 

##### 7. Start Geoserver

`cd ~/app/geoserver`
`sudo bash install_geoserver.sh`

##### 8. View GOAT in the browser

If all steps were successful you will be able to use GOAT when opening the index.html file in the front-end directory.

##### 9. Optional: Pre-calculate accessibility heat-map

GOAT allows you to use pre-calculated matrices that are used to visualize the dynamic heatmap. 
In order to start the pre-calculation you currently have to start the script manually with the following command:

`python3 ~/app/data_preparation/Python/precalculate_grid_thematic.py`

Depending on the size of your study area the calculation can take a bit.
You can also set different grid_sizes in the script.


###### 10. Connect to your database

You can connect to the PostgreSQL database with the following default credentials: 

**Change your credentials especially if you want to run GOAT in production**

Host: localhost
User: goat
Database: goat
Password: earlmanigault
Port: 65432




