---
title: Setup your own GOAT (recommended)
permalink: /docs/quick_start_docker/
---


GOAT<sub>beta</sub> is a web-application and is designed to feel at home on the Linux operating system. However, with the help of containers (Docker) and/or virtual machines (VM) you can install it on your Windows or Mac for development and testing.
You are supposed to type some commands into the command line, in case you are not familiar with the command line you can find many tutorials on the web. 


#### 1. Get a copy of GOAT<sub>beta</sub>

It is recommended to use Git for fetching the project.
Clone the GOAT-repo to a folder of your choice. Navigate first to the folder and run:

`git clone https://github.com/EPajares/goat.git` (run on your <span style="color:#07d">host</span>)

<img class="img-responsive" src="../../img/git_clone.png" alt="how your command window should look like" title="Get a copy of GOAT<sub>beta</sub>" width="600" height="400" style="border: 2px solid #07d;"/>



#### 2. Use Docker on your host to install software

<b>Install Docker & Docker-Compose</b>

Depending on your operating system there are different ways to install docker and docker-compose.

If you are on Windows follow:

[https://docs.docker.com/docker-for-windows/install/](https://docs.docker.com/docker-for-windows/install/) (Both docker and docker-compose are installed with the same installer)

As docker and docker-compose were originally build for the Linux OS, it could be that you experience issues, when installing Docker on your Windows machine. There are some common issues and possible solutions listed here:

[https://docs.docker.com/docker-for-windows/troubleshoot/](ttps://docs.docker.com/docker-for-windows/troubleshoot/)

In case you don't manage to install docker on your machine. You can follow the setup procedure described here: 

[Setup your own GOAT (alternative)](../quick_start_vm/)

#### 3. Configure GOAT<sub>beta</sub>

There is one key configuration file for setting up GOAT<sub>beta</sub>. You can find this file at `your-GOAT-directory/app/database/goat_config.yaml`.
At the moment not all configuration possibilities are in here but it is targeted to move more and more of the configuration in here.

It is recommended to open the files with a proper editor such as [Visual Studio Code](https://code.visualstudio.com/).

#### 4. Prepare your data

If you want to apply the tool to your own study area or adjust the input data, follow the description at [Data Preparation](../data_preparation/).

#### 5. Setup GOAT<sub>beta</sub>

Open a command window and go into the project folder. You will run all commands directly from your host. 

Install all the software and start services:

`docker-compose up -d` (This will start all service you need for goat (Database, Geoserver, NodeJS, etc.))

Fill and prepare the goat-database:

`docker exec -it goat-database python3 /opt/setup_goat.py` 

GOAT<sub>beta</sub> allows you to use pre-calculated matrices that are used to visualize the dynamic heatmaps. 
In order to start the pre-calculation you currently have to start the script manually with the following command:

`docker exec -it goat-database python3 /opt/data_preparation/Python/precalculate_grid_thematic.py`

Depending on the size of your study-area this can take some time. For Munich approx. 20 minutes.

For more Docker commands checkout:

[https://jstobigdata.com/docker-compose-cheatsheet/](https://jstobigdata.com/docker-compose-cheatsheet/)

##### 6. Connect to your database

You can connect to the PostgreSQL database with the following default credentials: 

**Change your credentials especially if you want to run GOAT<sub>beta</sub> in production**

Host: localhost

User: goat

Database: goat

Password: earlmanigault

Port: 65432

##### 7. Geoserver

The default password for your Geoserver instance is:

User: admin

Password : earlmanigault

You can access Geoserver by typing the following into your browser:

[http://localhost/geoserver](http://localhost/geoserver)

##### 8. View GOAT<sub>beta</sub> in the browser

If all steps were successful you will be able to use GOAT<sub>beta</sub> by typing the following into your browser:

[http://localhost](http://localhost)

##### 9. How start and stop GOAT<sub>beta</sub>

Navigate to your GOAT-folder (in this folder there should be the docker-compose.yml file)

<b>Stop<b>

`docker-compose down` (This will stop all running containers)

<b>Start<b>

`docker-compose up -d` (This will start all containers defined in the docker-compose.yml file)

##### 10. Backup Database

Per default the database is configured to run every day a backup at 11 PM. In case your database is not running at that time, the backup will be produced once you start GOAT.

In case you want an immediate backup you can simply run:

`docker exec -it goat-database-backup /bin/bash backups.sh`

##### 11. Update data

In case you want to update all your data you can simply run the following from your project directory:

`docker exec -it goat-database python3 /opt/setup_goat.py` 

<b><font color="red">!!Note this will drop your database and create a new database.!!</font><b>

Furthermore you need to run the pre-calculation script again in order to be able to use the heatmaps:

`docker exec -it goat-database python3 /opt/data_preparation/Python/precalculate_grid_thematic.py`
