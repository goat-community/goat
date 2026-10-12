#!/usr/bin/env bash
# The e2e stack's infrastructure: Postgres and Redis from the root
# compose.yaml, Garage for S3, Mailpit for mail and Keycloak with the compose
# bundle's realm. Reads its settings from the environment the e2e workflow
# sets (.github/workflows/e2e.yml), which starts it in the background.
#
# S3 is Garage, as in the compose bundle (deploy/compose): MinIO no longer
# publishes images, so the root compose.yaml's cannot be pulled. Keycloak is
# the GOAT image with the compose bundle's realm, as a self-hosted install
# runs it; it shares the compose Postgres, whose init creates the keycloak
# database. Mailpit catches the mail that core and Keycloak send
# (invitations, password setup).
set -euo pipefail

docker compose up -d --wait db redis
docker run -d --name garage -p 3900:3900 -p 3903:3903 \
  -e GARAGE_RPC_SECRET -e GARAGE_ADMIN_TOKEN \
  -v "$PWD/deploy/compose/init/garage/garage.toml:/etc/garage.toml:ro" \
  dxflrs/garage:v2.4.1
docker run -d --name mailpit -p 1025:1025 -p 8025:8025 axllent/mailpit:v1.27
docker run -d --name keycloak --network host \
  -e KEYCLOAK_DATABASE_VENDOR=postgresql -e KEYCLOAK_DATABASE_HOST=localhost \
  -e KEYCLOAK_DATABASE_PORT=5432 -e KEYCLOAK_DATABASE_NAME=keycloak \
  -e KEYCLOAK_DATABASE_USER="$POSTGRES_USER" -e KEYCLOAK_DATABASE_PASSWORD="$POSTGRES_PASSWORD" \
  -e KEYCLOAK_ADMIN=admin -e KEYCLOAK_ADMIN_PASSWORD="$E2E_KEYCLOAK_ADMIN_PASSWORD" \
  -e KEYCLOAK_EXTRA_ARGS=--import-realm -e KEYCLOAK_PRODUCTION=false \
  -e KEYCLOAK_ENABLE_HEALTH_ENDPOINTS=true -e KC_HOSTNAME_STRICT=false \
  -e GOAT_PUBLIC_URL=http://localhost:3000 -e GOAT_REALM=goat \
  -e GOAT_CLIENT_ID=goat -e GOAT_CLIENT_SECRET="$KEYCLOAK_CLIENT_SECRET" \
  -e GOAT_ADMIN_EMAIL=e2e-realm-admin@goat.test \
  -e GOAT_ADMIN_PASSWORD="$E2E_KEYCLOAK_ADMIN_PASSWORD" -e GOAT_SSL_REQUIRED=none \
  -e GOAT_SMTP_HOST=localhost -e GOAT_SMTP_PORT=1025 -e GOAT_SMTP_FROM=goat@e2e.test \
  -e GOAT_SMTP_FROM_NAME=GOAT -e GOAT_SMTP_AUTH=false -e GOAT_SMTP_USER= \
  -e GOAT_SMTP_PASSWORD= -e GOAT_SMTP_STARTTLS=false -e GOAT_SMTP_SSL=false \
  -v "$PWD/deploy/compose/init/keycloak/realm-goat.json:/opt/bitnami/keycloak/data/import/realm-goat.json:ro" \
  ghcr.io/plan4better/goat/keycloak:latest
