#! /usr/bin/env bash
set -e

python /app/src/celeryworker_pre_start.py

celery worker -A src.workers.celery_app -l info -c 1
