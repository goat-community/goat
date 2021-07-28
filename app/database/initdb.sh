#!/bin/bash
set -e

function update_database_with_postgis() {
    local db=$1
    echo "  Updating databse '$db' with extension"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$db" <<-EOSQL
        CREATE EXTENSION IF NOT EXISTS postgis;
EOSQL
}


if [ -n "$POSTGRES_DB_NAME" ]; then
	echo "Database creation requested: $POSTGRES_DB_NAME"
    update_database_with_postgis $POSTGRES_DB_NAME
	echo "Database created"
fi
