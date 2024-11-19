#!/bin/sh
# Skip if `.gitmodules` exists
[ -f .gitmodules ] && {
  echo ".gitmodules already initialized"
  exit 0
}

# Get the directory of the current script
SCRIPT_DIR="$(dirname "$0")"

"$SCRIPT_DIR"/git-setup.sh . goat-accounts::main::accounts
