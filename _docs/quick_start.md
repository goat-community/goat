---
title: Setup your own GOAT
permalink: /docs/quick_start/
---

For the developed Vagrant and Docker are used. It is recommended to use Git for fetching the project and if you are on Windows Git Bash is also a nice alternative to the windows command prompt. In order to start and customize GOAT for your study area, you have to follow these steps:

#### 1. Get a copy of GOAT

```
git clone https://github.com/EPajares/goat.git (run on your host or copy as zip-folder)
```


#### 2. Install Virtualbox
[https://www.virtualbox.org/](https://www.virtualbox.org/)

#### 3. Install Vagrant
It was only tested with the version mentioned above. Accordingly if you want to avoid unexpected issues, stick with that version.

[https://www.virtualbox.org/](https://www.vagrantup.com/)

#### 4. Prepare your data
Put all your data into the app/data folder!

##### If you want to disaggregate population data
You need a shapefile with administrative boundaries and a column with the number of inhabitants in this administrative unit, it works for any spatial resolution. The column has to be named “sum_pop” and has to be saved as integer. As the population data is used for population disaggregation, data on higher resolution will give you a more accurate disaggregation. Make sure you change the name of your spatial unit to name_administrative.

Optional: In the case you have custom landuse data you can place the data as shapefile (name the file: landuse.shp) into your data folder. The table has to include a column named "landuse". You can define in the table variable_container, which landuse category you want to exclude from the population disaggregation. For instance you can exclude graveyards or farmland and as consequences houses standing on these landuse categories are marked as not uninhabited.

##### If you already have population data on a high-resolution
Just place a shapefile called population.shp into your data folder. The geometry type has to be point and the number of residents have to be saved as integer into a column called "population".

#### 5. Define your bounding box and the OSM-Downloadlink
Open the file secret.js in the app/config folder. Customize the DOWNLOAD_LINK and define your BOUNDING_BOX.

#### 6. Setup GOAT
##### 6.1. Start Vagrant
Open a command window and go into the project folder. Run the command:

`vagrant up` (run on your host)

For more Vagrant commands checkout:

[https://gist.github.com/wpscholar/a49594e2e2b918f4d0c4](https://gist.github.com/wpscholar/a49594e2e2b918f4d0c4)

##### 6.2. Install the necessary software

`vagrant ssh` (run on your host)

`sudo bash app/installation/install_software.sh` (run on your VM)

This script can take a while as it installs quite some software on your VM. If you want to check what is installed exactly you can view the install_software.sh script.
This script can take a while as it installs quite some software on your VM. If you want to check what is installed exactly you can view the install_software.sh script.


##### 6.3. Fill your database

`sudo bash app/installation/setup_goat.sh` (run on your VM)

##### UPDATE data

In case you want to UPDATE all your data you can simply run the following from your project directory.

`sudo /etc/init.d/postgresql restart` (run on your VM)

`sudo bash app/installation/setup_goat.sh` (run on your VM)

!!Note this will drop your database and create a new database.!! 

##### 7. Start Geoserver

`cd ~/app/geoserver` (run on your VM)

`sudo bash install_geoserver.sh` (run on your VM)

Geoserver is running inside docker, which itself is inside your VM. You can check if Geoserver is up and running by typing `http://localhost:8080/geoserver/index.html` into your browser. The default password for your Geoserver instance is:

```
User: admin
Password : geoserver
```

##### 8. View GOAT in the browser


The front-end is bundled using parcel. At the moment it is recommended to run parcel on your host. For this you need to have NodeJS installed on your host:

[https://nodejs.org/en/](https://nodejs.org/en/)

In order to start the bundling go to the front-end directory and run:

`npm install` (run on your host)

`npm start` (run on your host)

If all steps were successful you will be able to use GOAT by typing the following into your browser:

[http://localhost:8585](http://localhost:8585)

You can also run parcel on your VM, however you have to open port 9090 and port 8585. This can be done on your Vagrantfile.

##### 9. Optional: Pre-calculate accessibility heat-map

GOAT allows you to use pre-calculated matrices that are used to visualize the dynamic heatmap. 
In order to start the pre-calculation you currently have to start the script manually with the following command:

`python3 ~/app/data_preparation/Python/precalculate_grid_thematic.py` (run on your VM)

Depending on the size of your study area the calculation can take a bit.

You can also set different grid_sizes in the script.


##### 10. Connect to your database

You can connect to the PostgreSQL database with the following default credentials: 

**Change your credentials especially if you want to run GOAT in production**

```
Host: localhost
User: goat
Database: goat
Password: earlmanigault
Port: 65432
```

##### Common Issues

If you use Windows as your host OS it might happen that you have issue when executing the shell scripts. Due to the different ways Unix-like systems and Windows are dealing with line endings. You will get an warning like "\r command not found". This especially happens if you open the shell scripts or the config.js with Wordpad or the text editor coming with Windows. You can avoid this by using an editor like Visual Studio Code. 
In the case you still face the issue you can convert the shell scripts and the secret.js with a tool like dos2unix.

You potentially have to run all the following commands:

`sudo apt install dos2unix` (run on your VM)

`dos2unix ~/app/installation/install_software.sh` (run on your VM)

`dos2unix ~/app/installation/setup_goat.sh` (run on your VM)

`dos2unix ~/app/config/secret.js` (run on your VM)

`dos2unix ~/app/geoserver/install_geoserver.sh` (run on your VM)



