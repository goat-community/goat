---
title: Setup your own GOAT (alternative)
permalink: /docs/quick_start_vm/
---


GOAT is a web-application and is designed to feel at home on the Linux operating system. However, with the help of containers (Docker) and/or virtual machines (VM) you can install it on your Windows or Mac for development and testing.

It is recommended to use Git for fetching the project and if you are on Windows Git Bash is also a nice alternative to the windows command prompt. The setup of GOAT is highly automated, though the user still has many customization options.

Git Bash Tutorial: [https://www.atlassian.com/git/tutorials/git-bash/](https://www.atlassian.com/git/tutorials/git-bash/)

#### 1. Get a copy of GOAT

Clone the GOAT-repo to a folder of your choice. Navigate first to the folder and run:

`git clone https://github.com/goat-community/goat.git` (run on your <span style="color:#07d">host</span>)

<img class="img-responsive" src="../../img/git_clone.png" alt="how your command window should look like" title="Get a copy of GOAT" width="600" height="400" style="border: 2px solid #07d;"/>


#### 2. Use a Virtual Machine to install Docker and the necessary software 

In case you don't manage to install docker on your Windows or MacOS host, it is recommended to use a Virtual Machine that is controlled by Vagrant. 

<b>Install Virtualbox (Version 5.2.18)<b>

[https://www.virtualbox.org/](https://www.virtualbox.org/)

Make sure that Hyper-V is enabled on your computer, i.e. it allows virtual machines to run.

<b>Install Vagrant (Version 2.2.2)<b>

[https://www.vagrantup.com/](https://www.vagrantup.com/)

It was only tested with the version mentioned above. Accordingly if you want to avoid unexpected issues, stick with these versions. Docker will be automatically installed on your VM.

#### 3. Configure GOAT

There is one key configuration file for setting up GOAT. You can find this file at `your-GOAT-directory/app/database/goat_config.yaml`.
At the moment not all configuration possibilities are in here but it is targeted to move more and more of the configuration in here.

It is recommended to open the files with a proper editor such as [Visual Studio Code](https://code.visualstudio.com/).

#### 4. Prepare your data

If you want to apply the tool to your own study area or adjust the input data, follow the description at [Data Preparation](../data_preparation/).

#### 5. Setup GOAT

##### 5.1. Start Vagrant

You will run similiar steps as in [Setup your own GOAT (recommended)](../setup_goat_docker/) but run everything within your VM.

Open a command window and go into the project folder. Run the command:

`vagrant up` (run on your <span style="color:#07d">host</span>)

<img class="img-responsive" src="../../img/vagrant_up.png" alt="how your command window should look like" title="Start vagrant" width="600" height="350" style="border: 2px solid #07d;"/>

Go into your VM:

`vagrant ssh` (run on your <span style="color:#07d">host</span>)

Install all the software and start services:

`sudo docker-compose up -d` (run on your <span style="color:#FE9A2E">VM</span>)(This will start all service you need for docker)

----

In case you receive the following error message: "Can't find a suitable configuration file in this directory or any parent. Are you in the right directory?", open your goat folder via the Windows or MacOS file explorer and copy the `docker-compose.yaml` file in the subfolder "app". 
Then run the following command on your <span style="color:#FE9A2E">VM</span>:

`cd app/`

`mv docker-compose.yaml ~`

`cd ..`

And run the `sudo docker-compose up -d` command again.

----

Fill and prepare the goat-database:

`sudo docker exec -it goat-database python3 /opt/setup_goat.py -t new_setup` (run on your <span style="color:#FE9A2E">VM</span>)

GOAT allows you to use pre-calculated matrices that are used to visualize the dynamic heatmaps. 
In order to start the pre-calculation you currently have to start the script manually with the following command:

`sudo docker exec -it goat-database python3 /opt/data_preparation/Python/precalculate_grid_thematic.py` (run on your <span style="color:#FE9A2E">VM</span>)

Depending on the size of your study-area this can take some time. For Munich approx. 20 minutes.

For more Docker commands checkout:

[https://jstobigdata.com/docker-compose-cheatsheet/](https://jstobigdata.com/docker-compose-cheatsheet/)

For more Vagrant commands checkout:

[https://gist.github.com/wpscholar/a49594e2e2b918f4d0c4](https://gist.github.com/wpscholar/a49594e2e2b918f4d0c4)


##### 6. Connect to your database

You can connect to the PostgreSQL database with the following default credentials: 

**Change your credentials especially if you want to run GOAT in production**

Host: localhost

User: goat

Database: goat

Password: earlmanigault

Port: 65432

##### 7. Geoserver

The default password for your Geoserver instance is:

User: admin

Password : geoserver

You can access Geoserver by typing the following into your browser:

[http://localhost:8080/geoserver](http://localhost/geoserver)

##### 8. View GOAT in the browser

If all steps were successful you will be able to use GOAT by typing the following into your browser:

[http://localhost:8080](http://localhost:8080)


##### 9. How start and stop GOAT

Navigate to your GOAT-folder (in this folder there should be the docker-compose.yml file)



<b>Stop<b>

`sudo docker-compose down` (run on your <span style="color:#FE9A2E">VM</span>) (This will stop all running containers)

`exit` (run on your <span style="color:#FE9A2E">VM</span>)

`vagrant halt` (run on your <span style="color:#07d">host</span>)

<b>Start<b>

`vagrant up` (run on your <span style="color:#07d">host</span>)

##### 10. Backup Database

Per default the database is configured to run every day a backup at 11 PM. In case your database is not running at that time, the backup will be produced once you start GOAT.

In case you want an immediate backup you can simply run:

`sudo docker exec -it goat-database-backup /bin/bash backups.sh` (run on your <span style="color:#FE9A2E">VM</span>)

##### 11. Update data

In case you want to update all your data you can simply run the following from your project directory:

`sudo docker exec -it goat-database python3 /opt/setup_goat.py` (run on your <span style="color:#FE9A2E">VM</span>)

<b><font color="red">!!Note this will drop your database and create a new database.!!</font><b>

Furthermore you need to run the pre-calculation script again in order to be able to use the heatmaps:

`sudo docker exec -it goat-database python3 /opt/data_preparation/Python/precalculate_grid_thematic.py` (run on your <span style="color:#FE9A2E">VM</span>)
