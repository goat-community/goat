#!/bin/sh
# Replaces the APP_NEXT_PUBLIC_* placeholders the image is built with by the
# container's NEXT_PUBLIC_* values, then runs the given command.
set -eu

WEB_DIR="${WEB_DIR:-/app/apps/web}"
NEXT_DIR="$WEB_DIR/.next"
TEMPLATES="$WEB_DIR/.next-templates.tar"

# The image keeps a pristine copy of every file that carries a placeholder.
# Restoring it first makes each start substitute the current values, so a
# changed value applies on a plain restart.
if [ -f "$TEMPLATES" ]; then
  tar -xf "$TEMPLATES" -C "$WEB_DIR"
fi

# A value escaped for the replacement side of `s|...|...|`.
sed_escape() {
  printf '%s\n' "$1" | sed -e 's/[\\&|]/\\&/g'
}

newline='
'

# Longest names first, so a name that extends another is replaced whole.
names=$(env | sed -n 's/^\(NEXT_PUBLIC_[A-Za-z0-9_]*\)=.*/\1/p' \
  | awk '{ print length($0), $0 }' | sort -rn | cut -d' ' -f2)

for name in $names; do
  # The name matches [A-Za-z0-9_]+, so the eval only reads that variable.
  eval "value=\${$name-}"
  case "$value" in
    *"$newline"*)
      echo "Skipping $name: values spanning several lines are not supported" >&2
      continue
      ;;
  esac
  escaped=$(sed_escape "$value")
  echo "Setting APP_$name"
  grep -rlF "APP_$name" "$NEXT_DIR" | while IFS= read -r file; do
    sed -i "s|APP_$name|$escaped|g" "$file"
  done
done

echo "Starting Nextjs"
exec "$@"
