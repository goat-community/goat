---
title: Setup your own GOAT<sub>beta</sub>
permalink: /docs/quick_start/
---


GOAT<sub>beta</sub> feels at home on the Linux distribution Ubuntu (18.04). However, with the help of an virtual machine (controlled by Vagrant) and with Docker you can offer GOAT<sub>beta</sub> a home also on your Windows or Mac OS for development and testing. It is recommended to use Git for fetching the project and if you are on Windows Git Bash is also a nice alternative to the windows command prompt. The setup of GOAT<sub>beta</sub> is highly automated, however the user has some customization options. Furthermore, it was decided to let the user type some commands on its own for allowing a more transparent and understandable setup. 

Git Bash Tutorial: [https://www.atlassian.com/git/tutorials/git-bash/](https://www.atlassian.com/git/tutorials/git-bash/)

If you have any issues during the process [Click Here](../common_issues/).

#### 1. Get a copy of GOAT<sub>beta</sub>

`git clone https://github.com/EPajares/goat.git` (run on your host)

#### 2. Install Software on your Host

<b>Install Virtualbox (Version 5.2.18)<b>

[https://www.virtualbox.org/](https://www.virtualbox.org/)

<b>Install Vagrant (Version 2.2.2)<b>

[https://www.vagrantup.com/](https://www.vagrantup.com/)

<b>Install NodeJS (Version 8.12.0)<b>

[https://nodejs.org/en/](https://nodejs.org/en/)


It was only tested with the version mentioned above. Accordingly if you want to avoid unexpected issues, stick with these versions.


#### 3. Configure GOAT<sub>beta</sub>

There is one central configuration file for setting up GOAT<sub>beta</sub>. You can find this file at `your-GOAT-directory/app/config/goat_config.yaml`.
At the moment not all configuration possibilities are in here but it is targeted to move more and more of the configuration in here. 

It is recommended not to open the files with your default editor as this may cause errors. Use editors such as [Visual Studio Code](https://code.visualstudio.com/) instead.

#### 4. Prepare your data

If you want to apply the tool to your own study area or adjust the input data, follow the descriptions in the following documentation: [Data Preparation](../data_preparation/)

#### 5. Setup GOAT<sub>beta</sub>

##### 5.1. Start Vagrant

Open a command window and go into the project folder. Run the command:

`vagrant up` (run on your <font color="RoyalBlue"> host</font>)

<img class="img-responsive" src="../../img/vagrant_up.png" alt="how your command window should look like" title="Start vagrant" width="600" height="350" style="border: 2px solid RoyalBlue;"/>

For more Vagrant commands checkout:

[https://gist.github.com/wpscholar/a49594e2e2b918f4d0c4](https://gist.github.com/wpscholar/a49594e2e2b918f4d0c4)

##### 5.2. Install the necessary software

`vagrant ssh` (run on your <font color="RoyalBlue"> host</font>)

`sudo bash app/installation/install_software.sh` (run on your <font color="chocolate"> VM</font>)

This script can take a while as it installs quite some software on your VM. If you want to check what is installed exactly you can view the install_software.sh script.

##### 5.3. Fill your database

`python3 app/installation/setup_goat.py` (run on your <font color="chocolate"> VM</font>)

##### UPDATE data

In case you want to UPDATE all your data you can simply run the following from your project directory.

`python3 app/installation/setup_goat.py` (run on your <font color="chocolate"> VM</font>)

<b><font color="red">!!Note this will drop your database and create a new database.!!</font><b>

##### 6. Connect to your database

You can connect to the PostgreSQL database with the following default credentials: 

**Change your credentials especially if you want to run GOAT<sub>beta</sub> in production**

Host: localhost

User: goat

Database: goat

Password: earlmanigault

Port: 65432


##### 7. Start Geoserver

`cd ~/app/geoserver` (run on your <font color="chocolate"> VM</font>)

`sudo bash install_geoserver.sh` (run on your <font color="chocolate"> VM</font>)

Geoserver is running inside docker, which itself is inside your VM. You can check if Geoserver is up and running by typing [http://localhost:8080/geoserver/index.html](http://localhost:8080/geoserver/index.html) into your browser. 
The default password for your Geoserver instance is:

User: admin

Password : geoserver

##### 8. Start Node-Server

`cd ~/app/node` (run on your <font color="chocolate"> VM</font>)

`npm install` (run on your <font color="chocolate"> VM</font>)

`npm start` (run on your <font color="chocolate"> VM</font>)

##### 9. View GOAT<sub>beta</sub> in the browser

The front-end is bundled using parcel. At the moment it is recommended to run parcel on your host. For this you need to have NodeJS installed on your host:

In order to start the bundling go to the front-end directory, open console window and run:

`npm install` (run on your <font color="RoyalBlue"> host</font>)

`npm start` (run on your <font color="RoyalBlue"> host</font>)

If all steps were successful you will be able to use GOAT<sub>beta</sub> by typing the following into your browser:

[http://localhost:8585](http://localhost:8585)

You can also run parcel on your VM, however you have to open port 9090 and port 8585. This can be done on your Vagrantfile.

##### 10. Optional: Pre-calculate accessibility heat-map

GOAT<sub>beta</sub> allows you to use pre-calculated matrices that are used to visualize the dynamic heatmaps. 
In order to start the pre-calculation you currently have to start the script manually with the following command:

`python3 ~/app/data_preparation/Python/precalculate_grid_thematic.py` (run on your VM)

Depending on the size of your study area the calculation can take a bit.

You can also set different grid_sizes in the script.

##### 11. How start and stop GOAT<sub>beta</sub>

<b>Stop<b>

After you have followed this documentation you will have two console windows open (one for the front-end and one for the NodeJS-server) you can kill the processes with Ctrl + c.  

If you want to turn your VM off: 

`cd your-GOAT-directory` (on your <font color="RoyalBlue"> host</font>)

`vagrant halt` (on your <font color="RoyalBlue"> host</font>)

Check for more vagrant commands: [https://www.vagrantup.com/docs/cli/](https://www.vagrantup.com/docs/cli/)

<b>Start<b>

If you want to start GOAT<sub>beta</sub> again. Simply open a command prompt and go to `your-GOAT-directory` and type `vagrant up`.
After some seconds you VM should be up an running. Your database and Geoserver are already up and running. However the front-end and the NodeJS-server you have to start manually. You have to repeat part of the procedure of 8. and 9.

Open a new console window and run the following:

`cd your-GOAT-directory/app/front_end` (on your <font color="RoyalBlue"> host</font>)

`npm start` (on your <font color="RoyalBlue"> host</font>)

<img class="img-responsive" src="../../img/start_frontend.png" alt="how your command window should look like" title="Start the front-end" width="600" height="340" style="border: 2px solid RoyalBlue;"/>

Open a new console window and run the following:

`cd your-GOAT-directory` (on your <font color="RoyalBlue"> host</font>)

`vagrant ssh` (on your <font color="RoyalBlue"> host</font>)

<img class="img-responsive" src="../../img/start_VM.png" alt="how your command window should look like" title="Start the VM" width="600" height="400" style="border: 2px solid RoyalBlue;"/>

`cd app/node` (run on your <span style="color:#01A9DB">VM</span>)

`npm start` (run on your <font color="chocolate">VM</font>)

<img class="img-responsive" src="../../img/start_nodeJS-server.png" alt="how your command window should look like" title="Start the NodeJS-server" width="600" height="260" style="border: 2px solid chocolate;"/>

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
