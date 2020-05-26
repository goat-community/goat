FROM python:3

RUN apt-get -y update && apt-get -y upgrade

# PYTHON AND DB DEPENDECIES
RUN apt-get install -y cron postgresql-client \
<<<<<<< HEAD
    && pip3 install  psycopg2-binary pyshp pyyaml requests
=======
    && pip3 install  psycopg2-binary pyshp pyyaml
>>>>>>> 787e7c3c818b887c335d5b49ac96f0ab667d833a

RUN touch /var/log/cron.log
COPY crontab /etc/cron.d/cjob
RUN chmod 0644 /etc/cron.d/cjob
ENV PYTHONUNBUFFERED 1
CMD cron -f