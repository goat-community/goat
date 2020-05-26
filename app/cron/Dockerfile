FROM python:3

RUN apt-get -y update && apt-get -y upgrade

# PYTHON AND DB DEPENDECIES
RUN apt-get install -y cron postgresql-client \
    && pip3 install  psycopg2-binary pyshp pyyaml

RUN touch /var/log/cron.log
COPY crontab /etc/cron.d/cjob
RUN chmod 0644 /etc/cron.d/cjob
ENV PYTHONUNBUFFERED 1
CMD cron -f