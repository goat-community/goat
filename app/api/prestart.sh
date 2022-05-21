#! /usr/bin/env bash

# Let the DB start
python /app/src/backend_pre_start.py

# # Run migrations
# alembic upgrade head

# Create initial data in DB
# python /app/src/initial_data.py
