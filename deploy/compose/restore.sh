#!/usr/bin/env bash
# Restores a backup made by the backup service into this deployment.
#   ./restore.sh backups/<timestamp>
# Stops GOAT, replaces the databases and volumes with the backup, starts GOAT.
set -euo pipefail
cd "$(dirname "$0")"
src=${1:?usage: ./restore.sh backups/<timestamp>}
src=$(cd "$src" && pwd)
[ -f "$src/goat.dump" ] || { echo "restore: $src/goat.dump not found" >&2; exit 1; }

read -r -p "This replaces ALL current GOAT data with $src. Type 'restore' to continue: " answer
[ "$answer" = restore ] || { echo "aborted"; exit 1; }

project=$(docker compose config --format json | jq -r .name)
docker compose down
docker compose up -d postgres
until docker compose exec -T postgres pg_isready -U goat -d goat -h 127.0.0.1 >/dev/null 2>&1; do sleep 2; done

for db in goat keycloak windmill; do
  [ -f "$src/$db.dump" ] || continue
  owner=goat; [ "$db" = goat ] || owner=$db
  docker compose exec -T postgres psql -U goat -d postgres -v ON_ERROR_STOP=1 \
    -c "DROP DATABASE IF EXISTS \"$db\" WITH (FORCE)" -c "CREATE DATABASE \"$db\" OWNER \"$owner\""
  docker compose exec -T postgres pg_restore -U goat -d "$db" --no-owner --role="$owner" < "$src/$db.dump"
done

restore_volume() {
  local volume="$1" archive="$2"
  [ -f "$archive" ] || return 0
  docker run --rm -v "${project}_${volume}:/v" -v "$(dirname "$archive"):/b:ro" alpine:3.22 \
    sh -c "find /v -mindepth 1 -delete && tar -C /v -xzf /b/$(basename "$archive")"
}
restore_volume goat-data "$src/goat-data.tar.gz"
restore_volume garage-meta "$src/garage-meta.tar.gz"
restore_volume garage-data "$src/garage-data.tar.gz"

docker compose up -d
echo "restore: done. Check with ./smoke.sh --quick"
