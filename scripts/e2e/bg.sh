#!/usr/bin/env bash
# Runs a setup task in the background, for a later step to await
# (scripts/e2e/await.sh): its output goes to logs/<name>.log and its exit
# code to logs/<name>.done when it ends. Used by .github/workflows/e2e.yml,
# whose setup tasks run side by side instead of one after another.
#
#   scripts/e2e/bg.sh <name> <command> [args...]
set -euo pipefail
name=$1
shift
mkdir -p logs
rm -f "logs/$name.done"
nohup bash -c '"$@" > "logs/$0.log" 2>&1; echo $? > "logs/$0.done"' "$name" "$@" > /dev/null 2>&1 &
echo "started $name in the background"
