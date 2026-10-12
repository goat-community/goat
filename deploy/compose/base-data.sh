#!/usr/bin/env bash
# Downloads the street network and public-transport base data that GOAT's
# routing tools (catchment areas, heatmaps, public-transport analyses) need.
# A full download is tens of GB; limit it to your region with --bbox.
#
#   ./base-data.sh --bbox 11.3,48.0,11.8,48.3          # Munich and surroundings
#   ./base-data.sh --datasets street_network --bbox ...
#   ./base-data.sh --dry-run                           # show what would be fetched
#   ./base-data.sh --bbox ... --weekly on|off          # also repeat this run every week
#
# Runs as a job in the running GOAT stack and follows it until it finishes.
set -euo pipefail
cd "$(dirname "$0")"

BBOX=""
DATASETS=""
DRY_RUN=false
WEEKLY=""

while [ $# -gt 0 ]; do
  case "$1" in
    --bbox) BBOX="$2"; shift 2 ;;
    --datasets) DATASETS="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    --weekly) WEEKLY="$2"; shift 2 ;;
    -h|--help) sed -n '2,11p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done
case "$WEEKLY" in ""|on|off) ;; *) echo "--weekly takes on or off" >&2; exit 2 ;; esac

# The tools image has Python and the Windmill token on the data volume; it
# reaches Windmill on the internal network, so the host needs nothing else.
docker compose run --rm --no-deps -T \
  -e BBOX="$BBOX" -e DATASETS="$DATASETS" -e DRY_RUN="$DRY_RUN" -e WEEKLY="$WEEKLY" \
  --entrypoint python windmill-sync - <<'PY'
import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE = f"{os.environ['WINDMILL_URL']}/api/w/{os.environ['WINDMILL_WORKSPACE']}"
TOKEN = open(os.environ["WINDMILL_TOKEN_FILE"]).read().strip()
SCRIPT = "f/goat/tasks/sync_base_data"
SCHEDULE = "f/goat/schedules/sync_base_data"


def call(method, path, body=None, raw=False):
    req = urllib.request.Request(
        BASE + path,
        data=None if body is None else json.dumps(body).encode(),
        method=method,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read().decode()
    return data if raw else (json.loads(data) if data else None)


params = {"dry_run": os.environ["DRY_RUN"] == "true"}
if os.environ["BBOX"]:
    params["bbox"] = [float(v) for v in os.environ["BBOX"].split(",")]
    if len(params["bbox"]) != 4:
        sys.exit("--bbox needs min_lon,min_lat,max_lon,max_lat")
if os.environ["DATASETS"]:
    params["datasets"] = [d.strip() for d in os.environ["DATASETS"].split(",") if d.strip()]

weekly = os.environ["WEEKLY"]
if weekly:
    # The weekly run repeats this run's region and data sets.
    call("POST", f"/schedules/update/{SCHEDULE}", {
        "schedule": "0 0 3 * * 2", "timezone": "UTC", "args": params,
        "script_path": SCRIPT, "is_flow": False,
    })
    call("POST", f"/schedules/setenabled/{SCHEDULE}", {"enabled": weekly == "on"})
    print(f"weekly base data update: {weekly}")

job = call("POST", f"/jobs/run/p/{SCRIPT}", params, raw=True).strip().strip('"')
print(f"base data job {job} started {json.dumps(params)}")
seen = 0
while True:
    time.sleep(5)
    try:
        logs = call("GET", f"/jobs_u/get_logs/{job}", raw=True)
    except urllib.error.HTTPError:
        logs = ""
    if len(logs) > seen:
        sys.stdout.write(logs[seen:])
        sys.stdout.flush()
        seen = len(logs)
    state = call("GET", f"/jobs_u/completed/get_result_maybe/{job}")
    if state and state.get("completed"):
        print()
        print(json.dumps(state.get("result"), indent=2)[:4000])
        sys.exit(0 if state.get("success") else 1)
PY
