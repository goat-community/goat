FROM postgres:11
ENV POSTGISV=2.5
ENV TZ=Europe/Berlin


RUN apt-get update \
   && apt-get install -y --no-install-recommends \
   postgresql-$PG_MAJOR-postgis-$POSTGISV \
   postgresql-$PG_MAJOR-postgis-$POSTGISV-scripts \ 
   postgresql-$PG_MAJOR-pgrouting \
   postgresql-$PG_MAJOR-pgrouting-scripts \
   postgresql-server-dev-$PG_MAJOR \
   &&  apt-get purge -y --auto-remove postgresql-server-dev-$PG_MAJOR

RUN apt install osmosis -y \
   &&  apt install osmctools -y \
   &&  apt install osm2pgsql -y \
   &&  apt install python3 -y \
   &&  apt install python3-pip -y \
   &&  apt install postgresql-plpython3-11 -y \
   &&  apt install wget \
   &&  pip3 install psycopg2-binary \
   &&  pip3 install pyshp \
   &&  pip3 install pyyaml 

RUN apt-get install -y cmake expat libexpat1-dev libboost-dev libboost-program-options-dev libpqxx-dev

ENV OSM_2_PGROUTING_VERSION=2.2.0
RUN apt install git -y \
   &&  git clone https://github.com/pgRouting/osm2pgrouting.git
RUN apt purge osm2pgrouting -y \
   &&  cd osm2pgrouting \
   &&  git fetch --all \
   &&  git checkout v${OSM_2_PGROUTING_VERSION} \
   &&  cmake -H. -Bbuild \
   &&  cd build/ \
   &&  make \
   &&  make install
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime &&  echo $TZ > /etc/timezone

#Exchange config files
#RUN cp ./pg_hba.conf /etc/postgresql/11/main/
#RUN cp ./postgresql.conf /etc/postgresql/11/main/
#RUN /etc/init.d/postgresql restart

# Add backup job
# RUN chmod +x /opt/pgbackup.sh

#VOLUME [/backups]