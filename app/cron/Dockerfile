FROM python:3


ENV APP_PATH /opt
WORKDIR ${APP_PATH}

COPY ./database $APP_PATH
RUN mkdir -p ${APP_PATH}/config
COPY ./config $APP_PATH/config

RUN apt-get -y update && apt-get -y upgrade
# PYTHON AND DB DEPENDECIES
RUN apt-get install -y cron postgresql-client \
    && pip3 install psycopg2-binary pyshp pyyaml requests

RUN touch /var/log/cron.log
COPY ./cron/crontab /etc/cron.d/cjob
RUN chmod 0644 /etc/cron.d/cjob
ENV PYTHONUNBUFFERED 1
CMD cron -f