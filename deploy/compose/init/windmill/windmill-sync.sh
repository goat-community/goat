#!/bin/sh
# Registers GOAT's analysis tools and scheduled tasks in Windmill. Safe to
# re-run: both sync commands update existing scripts and schedules in place.
set -eu

TOKEN_FILE="${WINDMILL_TOKEN_FILE:-/app/data/windmill/.token}"
if [ ! -s "$TOKEN_FILE" ]; then
  echo "windmill-sync: token file $TOKEN_FILE missing or empty" >&2
  exit 1
fi
TOKEN=$(cat "$TOKEN_FILE")
export TOKEN

python -m goatlib.tools.sync_windmill --url "$WINDMILL_URL" --workspace "$WINDMILL_WORKSPACE" --token "$TOKEN"
python -m goatlib.tasks.sync_windmill --url "$WINDMILL_URL" --workspace "$WINDMILL_WORKSPACE" --token "$TOKEN"
# The catalog mirror sync needs the GOAT data catalog bucket; without one it
# would fail on every run, so its schedule follows the configuration.
if [ -n "${CATALOG_S3_BUCKET:-}" ]; then enabled=true; else enabled=false; fi
python - "$enabled" <<'PY'
import json, os, sys, urllib.request

req = urllib.request.Request(
    f"{os.environ['WINDMILL_URL']}/api/w/{os.environ['WINDMILL_WORKSPACE']}"
    "/schedules/setenabled/f/goat/schedules/sync_catalog",
    data=json.dumps({"enabled": sys.argv[1] == "true"}).encode(),
    method="POST",
    headers={"Authorization": f"Bearer {os.environ['TOKEN']}", "Content-Type": "application/json"},
)
urllib.request.urlopen(req, timeout=30).read()
print(f"windmill-sync: sync_catalog schedule enabled={sys.argv[1]}")
PY
echo "windmill-sync: done"
