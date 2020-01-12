FROM kartoza/postgis:11.0-2.5

RUN apt update \ 
   &&  apt install osmosis -y \
   &&  apt install osmctools -y \
   &&  apt install osm2pgsql -y \
   &&  apt install python3 -y \
   &&  apt install python3-pip -y \
   &&  apt install postgresql-plpython3-11 -y \
   &&  apt install wget \
   &&  pip3 install psycopg2-binary \
   &&  pip3 install pyshp \
   &&  pip3 install pyyaml 

RUN wget http://security.ubuntu.com/ubuntu/pool/universe/b/boost1.62/libboost-program-options1.62.0_1.62.0+dfsg-5_amd64.deb \
   && dpkg -i libboost-program-options1.62.0_1.62.0+dfsg-5_amd64.deb \
   && wget http://ftp.br.debian.org/debian/pool/main/o/osm2pgrouting/osm2pgrouting_2.2.0-1_amd64.deb \
   && dpkg -i osm2pgrouting_2.2.0-1_amd64.deb

COPY database/pg_hba.conf /etc/postgresql/11/main/
COPY database/pg_hba.conf.template /etc/postgresql/11/main/
COPY database/postgresql.conf /etc/postgresql/11/main/

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime &&  echo $TZ > /etc/timezone

ENV APP_PATH /opt
WORKDIR ${APP_PATH}

COPY ./database $APP_PATH

RUN mkdir -p ${APP_PATH}/config
COPY ./config $APP_PATH/config
ADD ./database/setup-conf.sh /
