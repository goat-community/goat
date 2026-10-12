#!/bin/sh
# Nightly backup of the databases and data volumes into /backups/<timestamp>.
#   default:  wait for BACKUP_TIME every day
#   --now:    one backup, then exit (docker compose run --rm backup --now)
set -eu

RETENTION=${BACKUP_RETENTION_DAYS:-7}

run_backup() {
  ts=$(date -u +%Y%m%dT%H%M%SZ)
  dir="/backups/$ts.partial"
  mkdir -p "$dir"
  for db in goat keycloak windmill; do
    if psql -tAc "SELECT 1 FROM pg_database WHERE datname='$db'" | grep -q 1; then
      pg_dump -Fc -d "$db" -f "$dir/$db.dump"
    fi
  done
  tar -C /volumes/goat-data -czf "$dir/goat-data.tar.gz" .
  if [ -d /volumes/garage-data ] && [ -n "$(ls -A /volumes/garage-data 2>/dev/null)" ]; then
    # The live metadata database may be mid-write; the archive also holds
    # Garage's periodic snapshots (snapshots/), which are consistent copies.
    tar -C /volumes/garage-meta -czf "$dir/garage-meta.tar.gz" .
    tar -C /volumes/garage-data -czf "$dir/garage-data.tar.gz" .
  fi
  mv "$dir" "/backups/$ts"
  echo "backup: /backups/$ts ($(du -sh "/backups/$ts" | cut -f1))"
  find /backups -mindepth 1 -maxdepth 1 -type d -mtime +"$RETENTION" -exec rm -rf {} +
}

if [ "${1:-}" = "--now" ]; then
  run_backup
  exit 0
fi

target=${BACKUP_TIME:-02:30}
echo "backup: daily at $target UTC, keeping $RETENTION days"
while :; do
  now=$(date -u +%s)
  next=$(date -u -d "$(date -u +%Y-%m-%d) $target" +%s)
  [ "$next" -le "$now" ] && next=$((next + 86400))
  sleep $((next - now))
  run_backup || echo "backup: FAILED" >&2
done
