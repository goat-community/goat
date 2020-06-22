#FROM python:3
FROM goatcommunity/database:12-3-2.6.3-2.3.14

ENV APP_PATH /opt
WORKDIR ${APP_PATH}

COPY ./database $APP_PATH
RUN mkdir -p ${APP_PATH}/config
COPY ./config $APP_PATH/config

RUN apt-get -y update && apt-get -y upgrade
# PYTHON AND DB DEPENDECIES
#RUN apt-get install -y cron postgresql-client \
#    && pip3 install psycopg2-binary pyshp pyyaml requests boto3
RUN pip3 install requests boto3

RUN apt-get install cron
RUN touch /var/log/cron.log
COPY ./cron/crontab /etc/cron.d/cjob
RUN chmod 0644 /etc/cron.d/cjob
ENV PYTHONUNBUFFERED 1
ENTRYPOINT /usr/sbin/cron -f