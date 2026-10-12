#!/usr/bin/env bash
# Static checks of the GOAT Helm chart, the same ones CI runs:
#   helm lint, helm unittest, a render of every fixture under goat/ci/, and a
#   kubeconform schema check of each render.
# Needs helm (3.20), the helm-unittest plugin (1.1) and kubeconform.
#   ./deploy/helm/check.sh
set -euo pipefail

chart="$(cd "$(dirname "$0")" && pwd)/goat"
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT

helm dependency update "$chart" >/dev/null
helm lint --strict "$chart"
helm unittest "$chart"

for fixture in "$chart"/ci/*.yaml; do
  name=$(basename "$fixture" .yaml)
  helm template ci-render "$chart" -f "$fixture" > "$out/$name.yaml"
  echo "rendered $name: $(wc -l < "$out/$name.yaml") lines"
done

# CRDs are skipped: kubeconform has no schemas for them and they come
# verbatim from the pinned cloudnative-pg version. Custom resources
# (e.g. the CNPG `Cluster`) are still checked against the CRDs catalog.
for render in "$out"/*.yaml; do
  kubeconform -strict -kubernetes-version 1.30.0 \
    -skip CustomResourceDefinition \
    -schema-location default \
    -schema-location 'https://raw.githubusercontent.com/datreeio/CRDs-catalog/main/{{.Group}}/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json' \
    -summary "$render"
done
