---
title: Setup your own GOAT (alternative)
permalink: /docs/quick_start_vm/
---


GOAT<sub>beta</sub> is a web-application and is designed to feel at home on the Linux operating system. However, with the help of containers (Docker) and/or virtual machines (VM) you can install it on your Windows or Mac for development and testing.

It is recommended to use Git for fetching the project and if you are on Windows Git Bash is also a nice alternative to the windows command prompt. The setup of GOAT<sub>beta</sub> is highly automated, though the user still has many customization options.

Git Bash Tutorial: [https://www.atlassian.com/git/tutorials/git-bash/](https://www.atlassian.com/git/tutorials/git-bash/)

#### 1. Get a copy of GOAT<sub>beta</sub>

Clone the GOAT-repo to a folder of your choice. Navigate first to the folder and run:

`git clone https://github.com/EPajares/goat.git` (run on your <span style="color:#07d">host</span>)

<img class="img-responsive" src="../../img/git_clone.png" alt="how your command window should look like" title="Get a copy of GOAT<sub>beta</sub>" width="600" height="400" style="border: 2px solid #07d;"/>


#### 2 Use a Virtual Machine to install Docker and the necessary software 

In case you don't manage to install docker on your Windows or MacOS host, it is recommended to use a Virtual Machine that is controlled by Vagrant. 

<b>Install Virtualbox (Version 5.2.18)<b>

[https://www.virtualbox.org/](https://www.virtualbox.org/)

Make sure that Hyper-V is enabled on your computer, i.e. it allows virtual machines to run.

<b>Install Vagrant (Version 2.2.2)<b>

[https://www.vagrantup.com/](https://www.vagrantup.com/)

It was only tested with the version mentioned above. Accordingly if you want to avoid unexpected issues, stick with these versions. Docker will be automatically installed on your VM.

#### 3. Configure GOAT<sub>beta</sub>

There is one key configuration file for setting up GOAT<sub>beta</sub>. You can find this file at `your-GOAT-directory/app/database/goat_config.yaml`.
At the moment not all configuration possibilities are in here but it is targeted to move more and more of the configuration in here.

It is recommended to open the files with a proper editor such as [Visual Studio Code](https://code.visualstudio.com/).

#### 4. Prepare your data

If you want to apply the tool to your own study area or adjust the input data, follow the description at [Data Preparation](../data_preparation/).

#### 5. Setup GOAT<sub>beta</sub>

##### 5.1. Start Vagrant

You will run similiar steps as in [Setup your own GOAT (recommended)](../setup_goat_docker/) but run everything within your VM.

Open a command window and go into the project folder. Run the command:

`vagrant up` (run on your <span style="color:#07d">host</span>)

<img class="img-responsive" src="../../img/vagrant_up.png" alt="how your command window should look like" title="Start vagrant" width="600" height="350" style="border: 2px solid #07d;"/>

Go into your VM:

`vagrant ssh` (run on your <span style="color:#07d">host</span>)

Install all the software and start services:

`docker-compose up -d` (run on your <span style="color:#FE9A2E">VM</span>)(This will start all service you need for docker)

Fill and prepare the goat-database:

`docker exec -it goat-database python3 /opt/setup_goat.py` (run on your <span style="color:#FE9A2E">VM</span>)

GOAT<sub>beta</sub> allows you to use pre-calculated matrices that are used to visualize the dynamic heatmaps. 
In order to start the pre-calculation you currently have to start the script manually with the following command:

`docker exec -it goat-database python3 /opt/data_preparation/Python/precalculate_grid_thematic.py` (run on your <span style="color:#FE9A2E">VM</span>)

Depending on the size of your study-area this can take some time. For Munich approx. 20 minutes.

`docker exec -it goat-database python3 /opt/setup_goat.py` (run on your <span style="color:#FE9A2E">VM</span>)

For more Docker commands checkout:

[https://jstobigdata.com/docker-compose-cheatsheet/](https://jstobigdata.com/docker-compose-cheatsheet/)

For more Vagrant commands checkout:

[https://gist.github.com/wpscholar/a49594e2e2b918f4d0c4](https://gist.github.com/wpscholar/a49594e2e2b918f4d0c4)


##### 5.2. Install the necessary software

`docker-compose up -d` (run on your <span style="color:#07d">host</span>)

##### 5.3. Fill your database

`docker exec -it goat-database python3 /opt/setup_goat.py` (run on your <span style="color:#FE9A2E">VM</span>)

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

Password : geoserver

##### 8. View GOAT<sub>beta</sub> in the browser

If all steps were successful you will be able to use GOAT<sub>beta</sub> by typing the following into your browser:

Docker on host:

[http://localhost](http://localhost)

With Virtual Machine:

[http://localhost:8080](http://localhost:8080)

##### 10. Optional: Pre-calculate accessibility heat-map

GOAT<sub>beta</sub> allows you to use pre-calculated matrices that are used to visualize the dynamic heatmaps. 
In order to start the pre-calculation you currently have to start the script manually with the following command:

`python3 ~/app/data_preparation/Python/precalculate_grid_thematic.py` (run on your <span style="color:#FE9A2E">VM</span>)

Depending on the size of your study area the calculation can take a bit.

You can also set different grid_sizes in the script.

##### 11. How start and stop GOAT<sub>beta</sub>

<b>Stop<b>

After you have followed this documentation you will have two console windows open (one for the front-end and one for the NodeJS-server) you can kill the processes with Ctrl + c.  

If you want to turn your VM off: 

`cd your-GOAT-directory` (on your <span style="color:#07d">host</span>)

`vagrant halt` (on your <span style="color:#07d">host</span>)

<img class="img-responsive" src="../../img/vagrant_halt.png" alt="how your command window should look like" title="How to turn off your VM" width="600" style="border: 2px solid #07d;"/>

Check for more vagrant commands: [https://www.vagrantup.com/docs/cli/](https://www.vagrantup.com/docs/cli/)

<b>Start<b>

If you want to start GOAT<sub>beta</sub> again. Simply open a command prompt and go to `your-GOAT-directory` and type `vagrant up`.
After some seconds you VM should be up an running. Your database and Geoserver are already up and running. However the front-end and the NodeJS-server you have to start manually. You have to repeat part of the procedure of 8. and 9.

Open a new console window and run the following:

`cd your-GOAT-directory/app/front_end` (on your <span style="color:#07d">host</span>)

`npm start` (on your <span style="color:#07d">host</span>)

<img class="img-responsive" src="../../img/start_frontend.png" alt="how your command window should look like" title="Start the front-end" width="600" height="340" style="border: 2px solid #07d;"/>

Open a new console window and run the following:

`cd your-GOAT-directory` (on your <span style="color:#07d">host</span>)

`vagrant ssh` (on your <span style="color:#07d">host</span>)

<img class="img-responsive" src="../../img/start_VM.png" alt="how your command window should look like" title="Start the VM" width="600" height="400" style="border: 2px solid #07d;"/>

`cd app/node` (run on your <span style="color:#FE9A2E">VM</span>)

`npm start` (run on your <span style="color:#FE9A2E">VM</span>)

<img class="img-responsive" src="../../img/start_nodeJS-server.png" alt="how your command window should look like" title="Start the NodeJS-server" width="600" height="260" style="border: 2px solid #FE9A2E;"/>

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


##### Update data

In case you want to update all your data you can simply run the following from your project directory.

`python3 app/installation/setup_goat.py` (run on your <span style="color:#FE9A2E">VM</span>)

<b><font color="red">!!Note this will drop your database and create a new database.!!</font><b>
