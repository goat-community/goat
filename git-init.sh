#!/bin/sh
# Skip if `.gitmodules` exists
[ -f .gitmodules ] && {
  echo ".gitmodules already initialized"
  exit 0
}

./git-setup.sh goat-accounts::main::accounts
