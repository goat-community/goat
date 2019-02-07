cd /home/vagrant
sudo apt install wget

#Install PostGreSQL, PostGIS, pgRouting and osm2pgrouting (source)
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt bionic-pgdg main" >> /etc/apt/sources.list'
wget --quiet -O - http://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc | sudo apt-key add -
sudo apt update
sudo apt install postgresql-10 -y
sudo apt install postgresql-10-postgis-2.4 -y
sudo apt install postgresql-10-postgis-scripts -y
sudo apt install postgresql-plpython3-10
#to get the commandline tools shp2pgsql, raster2pgsql you need to do this
sudo apt install postgis -y
sudo apt install postgresql-10-pgrouting -y
sudo apt install osmosis -y
sudo apt install osm2pgsql -y
sudo apt purge osm2pgrouting -y

#Install Python packages
sudo apt install python3-pip -y
pip3 install psycopg2-binary
pip3 install pyshp

cd app

#Libraries for compiling osm2pgrouting
sudo apt install libblkid-dev e2fslibs-dev libaudit-dev libexpat1-dev -y
sudo apt install libboost-all-dev -y
sudo apt install expat -y
sudo apt install libexpat1-dev -y
sudo apt install libboost-program-options-dev -y
sudo apt install libpqxx-dev -y
sudo apt install cmake -y

#Install osm2pgrouting from source
wget https://github.com/pgRouting/osm2pgrouting/archive/v2.2.0.zip
unzip v2.2.0.zip
cd osm2pgrouting-2.2.0/
cmake -H. -Bbuild
cd build/
sudo make
sudo make install
cd /home/vagrant/app
rm -r osm2pgrouting-2.2.0
rm v2.2.0.zip
#Exchange config files
sudo cp config/pg_hba.conf /etc/postgresql/10/main/
sudo cp config/postgresql.conf /etc/postgresql/10/main/
sudo /etc/init.d/postgresql restart

#### Install Docker-CE

echo "Install Docker-CE"

apt-get -y UPDATE

apt-get -y install \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -

add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

apt-get -y update

apt-get -y install docker-ce


#Install NodeJS (currently not on docker container as nodemon was not working properly)
curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
sudo apt install -y nodejs

sudo apt install osmctools