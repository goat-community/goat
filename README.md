# Geo Open Accessibility Tool (GOAT)

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

Openlayers 5

Parcel

NodeJS 8.12.0

Virtual Box 5.2.18

Vagrant 2.1.2

Docker

## Setup GOAT

For the developed Vagrant and Docker are used. In order to start and customize GOAT for your study area you have to follow these steps:

#### 1. Get a copy of GOAT

`git clone https://github.com/EPajares/goat.git` 

or copy as zip-folder

#### 2. Install Virtualbox

https://www.virtualbox.org/

#### 3. Install Vagrant

https://www.vagrantup.com/

#### 4. Prepare your data

Put all your data into the data folder!

##### If you want to disaggregate population data

You need a shapefile with administrative boundaries and a column with the number of inhabitants in this administrative 
unit, it works for any spatial resolution. The column has to be named “sum_pop” and has to be saved as integer. 
As the population data is used for population disaggregation, data on higher resolution will give you a more 
accurate disaggregation.

Optional: In the case you have custom landuse data you can place the data as shapefile (name the file: landuse.shp) into your data folder. The table has to include a column named "landuse". You can define in the table variable_container, which landuse category you want to exclude from the population disaggregation. For instance you can exclude graveyards or farmland and as consequences houses standing on these landuse categories are marked as not uninhabited. 

##### If you already have population data on a high-resolution

Just place a shapefile called population.shp into your data folder. The geometry type has to be point and the number of residents have to be saved as integer into a column called "population". 


#### 5. Define your bounding box and the OSM-Downloadlink

Open the file secret.js in the config folder. Customize the DOWNLOAD_LINK and define your BOUNDING_BOX.

#### 6. Setup GOAT

##### 6.1. Start Vagrant

Open a command window and go into the project folder. Run the command:

`vagrant up`

For more Vagrant commands checkout:

https://gist.github.com/wpscholar/a49594e2e2b918f4d0c4

##### 6.2. Install the necessary software

`sudo bash app/installation/install_software.sh`

This script can take a while as it installs quite some software on your VM. If you want to check what is installed exactly you can view the install_software.sh script.

##### 6.3. Fill your database

`vagrant ssh`

`sudo bash app/installation/setup_goat.sh`

##### UPDATE data

In case you want to UPDATE all your data you can simply run the following from your project directory.

`sudo /etc/init.d/postgresql restart`

`sudo bash app/installation/setup_goat.sh`

Note this will drop your database and create a new database. 

##### 7. Start Geoserver

`cd ~/app/geoserver`

`sudo bash install_geoserver.sh`

Geoserver is running inside docker, which itself is inside the VM.

##### 8. View GOAT in the browser


The front-end is bundled using parcel. In order to start the bundling go to the front-end directory and run:

`npm install`

`npm start`

If all steps were successful you will be able to use GOAT by typing the following into your browser:

http://localhost:8585

You can run the bundeling inside your VM or on your host. The built-in watch functionality provided by parcel is at the moment only working, when you run it on your host.

##### 9. Optional: Pre-calculate accessibility heat-map

GOAT allows you to use pre-calculated matrices that are used to visualize the dynamic heatmap. 
In order to start the pre-calculation you currently have to start the script manually with the following command:

`python3 ~/app/data_preparation/Python/precalculate_grid_thematic.py`

Depending on the size of your study area the calculation can take a bit.

You can also set different grid_sizes in the script.


##### 10. Connect to your database

You can connect to the PostgreSQL database with the following default credentials: 

**Change your credentials especially if you want to run GOAT in production**

Host: localhost

User: goat

Database: goat

Password: earlmanigault

Port: 65432

##### Common Issues

If you use Windows as your host OS it might happen that you have issue when executing the shell scripts. Due to the different ways Unix-like systems and Windows are dealing with line endings. You will get an warning like "\r command not found". In order to convert the shell scripts to files the Linux-VM can execute you may have to convert the files first. You can use a tool like dos2unix.

You potentially have to run all the following commands:

`sudo apt install dos2unix`

`dos2unix ~/app/installation/install_software.sh`

`dos2unix ~/app/installation/setup_goat.sh`

`dos2unix ~/app/config/secret.js`

`dos2unix ~/app/geoserver/install_geoserver.sh`
