#!/bin/sh
# Starts Keycloak with the certificates in GOAT_CA_BUNDLE trusted on top of the
# JDK's public CAs, so it can send email through a relay whose certificate
# comes from a company CA. Without GOAT_CA_BUNDLE Keycloak starts unchanged.
set -eu

if [ -n "${GOAT_CA_BUNDLE:-}" ]; then
  if [ ! -r "$GOAT_CA_BUNDLE" ]; then
    echo "truststore.sh: GOAT_CA_BUNDLE $GOAT_CA_BUNDLE is not readable" >&2
    exit 1
  fi
  store=/tmp/goat-truststore.p12
  # Holds public certificates only, so the password protects nothing.
  pass=goat-truststore
  rm -f "$store"
  keytool -importkeystore -noprompt \
    -srckeystore "${JAVA_HOME:-/opt/bitnami/java}/lib/security/cacerts" -srcstorepass changeit \
    -destkeystore "$store" -deststoretype PKCS12 -deststorepass "$pass" >/dev/null 2>&1
  # keytool reads one certificate per file, so split the bundle.
  dir=$(mktemp -d)
  awk -v dir="$dir" '
    /-----BEGIN CERTIFICATE-----/ { n++; file = sprintf("%s/ca-%03d.pem", dir, n) }
    file { print > file }
    /-----END CERTIFICATE-----/ { close(file); file = "" }
  ' "$GOAT_CA_BUNDLE"
  count=0
  for cert in "$dir"/ca-*.pem; do
    [ -e "$cert" ] || continue
    keytool -importcert -noprompt -trustcacerts -alias "goat-$(basename "$cert" .pem)" \
      -file "$cert" -keystore "$store" -storepass "$pass" >/dev/null
    count=$((count + 1))
  done
  rm -rf "$dir"
  if [ "$count" -eq 0 ]; then
    echo "truststore.sh: no certificate found in $GOAT_CA_BUNDLE" >&2
    exit 1
  fi
  echo "truststore.sh: trusting $count certificate(s) from $GOAT_CA_BUNDLE"
  export KEYCLOAK_SPI_TRUSTSTORE_FILE="$store"
  export KEYCLOAK_SPI_TRUSTSTORE_PASSWORD="$pass"
fi

exec /opt/bitnami/scripts/keycloak/entrypoint.sh "$@"
