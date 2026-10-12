#!/bin/sh
# First start only (empty data directory): databases, roles and extensions
# for GOAT, Windmill and Keycloak.
set -eu

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
  -v windmill_pw="$WINDMILL_DB_PASSWORD" -v keycloak_pw="$KEYCLOAK_DB_PASSWORD" <<'SQL'
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Windmill's migrations grant to these two roles and expect them to exist.
CREATE ROLE windmill_user NOLOGIN;
CREATE ROLE windmill_admin NOLOGIN BYPASSRLS IN ROLE windmill_user;
CREATE ROLE windmill LOGIN CREATEDB PASSWORD :'windmill_pw' IN ROLE windmill_admin, windmill_user;
CREATE DATABASE windmill OWNER windmill;
ALTER ROLE windmill IN DATABASE windmill SET search_path = public;

CREATE ROLE keycloak LOGIN PASSWORD :'keycloak_pw';
CREATE DATABASE keycloak OWNER keycloak;
SQL
