---
title: Setup your own GOAT
permalink: /docs/quick_start/
---


GOAT feels at home on the Linux distribution Ubuntu (18.04). However, with the help of an virtual machine (controlled by Vagrant) and with Docker you can offer GOAT a home also on your Windows or Mac OS for development and testing. It is recommended to use Git for fetching the project and if you are on Windows Git Bash is also a nice alternative to the windows command prompt.
The setup of GOAT is highly automated, however the user has some customization options. Furthermore, it was decided to let the user type some commands on its own for allowing a more transparent and understandable setup. 

#### 1. Get a copy of GOAT

`git clone https://github.com/EPajares/goat.git` (run on your host)

#### 2. Install Software on your Host

<b>Install Virtualbox (Version 5.2.18)<b>

[https://www.virtualbox.org/](https://www.virtualbox.org/)

<b>Install Vagrant (Version 2.2.2)<b>

[https://www.vagrantup.com/](https://www.vagrantup.com/)

<b>Install NodeJS (Version 8.12.0)<b>

[https://nodejs.org/en/](https://nodejs.org/en/)


It was only tested with the version mentioned above. Accordingly if you want to avoid unexpected issues, stick with these versions.


#### 3. Configure GOAT

There is one central configuration file for setting up GOAT. You can find this file at `your-GOAT-directory/app/config/goat_config.yaml`.
At the moment not all configuration possibilities are in here but it is targeted to move more and more of the configuration in here. 

#### 4. Prepare your data

<b>Necessary shapefile<b>

study_area.shp

There is one folder (your-GOAT-directory/app/data) in which you can organize the data you want to load into the database. 
The setup-script will search for shapefiles in this directory and upload all of them into your database. The only file that is essential for setting up GOAT is a shapefile defining your study area. Other data is optional, however especially landuse data or custom population data can improve data quality.
As high-resolution population data is one of most important data source for GOAT there are three different ways for you to feed the data into the system. Depending on your data availability you can pick one approach in the `your-GOAT-directory/app/config/goat_config.yaml`.

##### Population disaggregation

<b>Custom data<b>

landuse.shp (optional)

Two SQL-scripts do the job for you:

The script `your-GOAT-directory/app/data_preparation/SQL/buildings_residential.sql` will extract all the residential buildings from the planet_osm_polygon-table (this table contains all OSM-polygons in you study area and will be created automatically). As OSM data is of varying quality and tagging-schemes are not always consistent there are several attributes on which this extraction can be done. In addition a custom landuse-table can help to select only residential buildings. You can customize the settings for this extraction in the table variable_container either before the setup `your-GOAT-directory/app/data_preparation/SQL/create_tables.sql` but also afterwards to tune you disaggregation. 

There is a second script `your-GOAT-directory/app/data_preparation/SQL/population_disaggregation.sql` actually disaggregates the population data from the boundaries you added with your study_area to the individual buildings. As the population disaggregation is based on OpenStreetMap data, it relies on relatively complete OSM-buildings footprints. In addition, especially in areas with heterogenous building levels it is recommended to check if buildings levels are mapped properly. If there are no buildings levels mapped a default value, which can be defined by you in the database table `variable_container` will be used. 

In general it is highly recommended to check for the data quality in your study area. If you are unhappy with the data quality it is highl recommended to improve the local OSM dataset. Very often with some little mapping effort you can improve data quality essentially. The setup of GOAT allows you to update the data after successful mapping. 


##### Census extrapolation 

<b>Custom data<b>

census.shp

landuse.shp (optional)

In the case you have census data in your study area but you know the data is outdated. GOAT has an script `your-GOAT-directory/app/data_preparation/SQL/census.sql` that allows you to update the census grids based on current population numbers in your whole study area. The script checks for areas where new development took place and estimates based on average gross living area how many residents live in the affected grids. You can also customize the same in the `variable_container`. This procedure also makes use of the extracted residential buildings as described in the population dissagregation.

##### Custom high-resolution population data 

<b>Custom data<b>

population.shp

If you have population data as point source you can upload the same into the database.


##### Filename conventions

The automated way the scripts process the data make it necessary that the your custom data is labelled correctly. It is important the filename and certain attributes are labelled as in the following examples. It is possible to import shapefiles with additional columns however it is important that the folowing conventions are followed. 

<img class="img-responsive" src="../../img/shapefile_study_area.png" alt="how your study area shapefile has to be for GOAT" title="Shapefile study area">

<b>Name the file <font color="red">study_area.shp</font> and make sure the columns <font color="red">sum_pop</font> and <font color="red">name</font> are existing!<b>

<img class="img-responsive" src="../../img/shapefile_landuse.png" alt="how your landuse shapefile has to be for GOAT" title="Shapefile landuse">

<b>Name the file <font color="red">landuse.shp</font> and make sure the column <font color="red">landuse</font> is existing!<b>

<img class="img-responsive" src="../../img/shapefile_census.png" alt="how your census shapefile has to be for GOAT" title="Shapefile census">

<b>Name the file <font color="red">census.shp</font> and make sure the column <font color="red">pop</font> is existing!<b>

<img class="img-responsive" src="../../img/shapefile_population.png" alt="how your population shapefile has to be for GOAT" title="Shapefile population">

<b>Name the file <font color="red">population.shp</font> and make sure the column <font color="red">population</font> is existing!<b>


You can furthermore permanently upload additional data into your database with the command-line tools shp2pgsql or others.

#### 5. Setup GOAT

##### 5.1. Start Vagrant

Open a command window and go into the project folder. Run the command:

`vagrant up` (run on your host)

For more Vagrant commands checkout:

[https://gist.github.com/wpscholar/a49594e2e2b918f4d0c4](https://gist.github.com/wpscholar/a49594e2e2b918f4d0c4)

##### 5.2. Install the necessary software

`vagrant ssh` (run on your host)

`sudo bash app/installation/install_software.sh` (run on your VM)

This script can take a while as it installs quite some software on your VM. If you want to check what is installed exactly you can view the install_software.sh script.

##### 5.3. Fill your database

`python3 app/installation/setup_goat.py` (run on your VM)

##### UPDATE data

In case you want to UPDATE all your data you can simply run the following from your project directory.

`python3 app/installation/setup_goat.py` (run on your VM)

<b><font color="red">!!Note this will drop your database and create a new database.!!</font><b>

##### 6. Connect to your database

You can connect to the PostgreSQL database with the following default credentials: 

**Change your credentials especially if you want to run GOAT in production**

Host: localhost

User: goat

Database: goat

Password: earlmanigault

Port: 65432


##### 7. Start Geoserver

`cd ~/app/geoserver` (run on your VM)

`sudo bash install_geoserver.sh` (run on your VM)

Geoserver is running inside docker, which itself is inside your VM. You can check if Geoserver is up and running by typing [http://localhost:8080/geoserver/index.html](http://localhost:8080/geoserver/index.html) into your browser. 
The default password for your Geoserver instance is:

User: admin

Password : geoserver

##### 8. View GOAT in the browser


The front-end is bundled using parcel. At the moment it is recommended to run parcel on your host. For this you need to have NodeJS installed on your host:

In order to start the bundling go to the front-end directory and run:

`npm install` (run on your host)

`npm start` (run on your host)

If all steps were successful you will be able to use GOAT by typing the following into your browser:

[http://localhost:8585](http://localhost:8585)

You can also run parcel on your VM, however you have to open port 9090 and port 8585. This can be done on your Vagrantfile.

##### 9. Optional: Pre-calculate accessibility heat-map

GOAT allows you to use pre-calculated matrices that are used to visualize the dynamic heatmaps. 
In order to start the pre-calculation you currently have to start the script manually with the following command:

`python3 ~/app/data_preparation/Python/precalculate_grid_thematic.py` (run on your VM)

Depending on the size of your study area the calculation can take a bit.

You can also set different grid_sizes in the script.


##### Common Issues

If you use Windows as your host OS it might happen that you have issue when executing the shell scripts. Due to the different ways Unix-like systems and Windows are dealing with line endings. You will get an warning like "\r command not found". This especially happens if you open the shell scripts or the config.js with Wordpad or the text editor coming with Windows. You can avoid this by using an editor like Visual Studio Code. 
In the case you still face the issue you can convert the shell scripts and the secret.js with a tool like dos2unix.

You potentially have to run all the following commands:

`sudo apt install dos2unix` (run on your VM)

`dos2unix ~/app/installation/install_software.sh` (run on your VM)

`dos2unix ~/app/installation/setup_goat.sh` (run on your VM)

`dos2unix ~/app/config/goat_config.yaml` (run on your VM)

`dos2unix ~/app/geoserver/install_geoserver.sh` (run on your VM)

##### Backup Database

Make backup directory

`sudo mkdir /var/lib/postgresql/backup`

Login as root user:

`sudo su`

Login as user postgres:

`su - postgres`

Open the crontab for the postgres user:

`crontab -e`

Add these lines to crontab file for having a backup every second day (they can be customized):

1 * * * 1 pg_dump -U postgres goat > /var/lib/postgresql/backup/backup_last_monday.sql

1 * * * 3 pg_dump -U postgres goat > /var/lib/postgresql/backup/backup_last_wednesday.sql

1 * * * 5 pg_dump -U postgres goat > /var/lib/postgresql/backup/backup_last_friday.sql

1 * * * 7 pg_dump -U postgres goat > /var/lib/postgresql/backup/backup_last_sunday.sql

Checkout: [https://crontab.guru/](https://crontab.guru/)
