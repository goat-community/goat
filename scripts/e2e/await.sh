#!/usr/bin/env bash
# Waits for a task started with scripts/e2e/bg.sh. Fails, showing the end of
# the task's log, when it failed or did not end within the given seconds.
#
#   scripts/e2e/await.sh <name> <timeout-seconds>
set -euo pipefail
name=$1
limit=$2
waited=0
until [ -f "logs/$name.done" ]; do
  if [ "$waited" -ge "$limit" ]; then
    echo "::error::$name did not finish within ${limit}s"
    tail -40 "logs/$name.log" || true
    exit 1
  fi
  sleep 2
  waited=$((waited + 2))
done
code=$(cat "logs/$name.done")
if [ "$code" != 0 ]; then
  echo "::error::$name failed (exit $code)"
  tail -60 "logs/$name.log" || true
  exit "$code"
fi
echo "$name done after ${waited}s of waiting"
