# GOAT Helm chart

The chart itself, with every value and the upgrade notes, is in
[`goat/`](goat/) ([README](goat/README.md)). It is published as
`oci://ghcr.io/plan4better/charts/goat`:

```bash
helm install goat oci://ghcr.io/plan4better/charts/goat \
  --namespace goat --create-namespace --values your-values.yaml --wait --timeout 25m
```

The [Kubernetes page](https://goat.plan4better.de/docs/self_hosting/kubernetes)
of the documentation summarises what the chart includes and what you provide.

## Checks

```bash
./deploy/helm/check.sh       # helm lint, helm unittest, render + kubeconform every goat/ci/ fixture
./deploy/helm/smoke-k3d.sh   # install on a throwaway k3d cluster, upgrade, check every service
```

`check.sh` needs Helm 3.20, the helm-unittest plugin 1.1 and kubeconform, the
versions CI pins in [`.github/actions/helm-tools`](../../.github/actions/helm-tools/action.yml).
It runs on every pull request that touches `deploy/helm/` and on every push to
`main`. The smoke test builds a cluster and pulls every GOAT image, so CI runs
it for every chart release tag, before publishing, and when the
[Helm chart workflow](../../.github/workflows/helm.yml) is started by hand
(*Actions → Helm chart → Run workflow*, on any branch).

## Releases

The chart has its own version (`version` in [`goat/Chart.yaml`](goat/Chart.yaml)),
separate from the GOAT release it installs (`appVersion`).

1. Raise `version` (and `appVersion` for a new GOAT release), add a row to the
   version history in the chart README.
2. Tag the commit `helm-<version>`, e.g. `git tag -s helm-0.5.2 -m "helm 0.5.2"`,
   and push the tag.

The tag's workflow checks that it matches `Chart.yaml`, runs the checks and the
smoke test, and only when both pass pushes the package to ghcr.io and signs it
with cosign (keyless). A failed smoke test publishes nothing: fix it, and move
the tag to the fixed commit. It creates no GitHub release: the
repository's releases are GOAT releases, and the chart's changes are in the
version history of its README. Every published version is listed on the
[package page](https://github.com/orgs/plan4better/packages/container/package/charts%2Fgoat).

To verify a chart's signature:

```bash
cosign verify ghcr.io/plan4better/charts/goat:<version> \
  --certificate-identity-regexp '^https://github.com/plan4better/goat/.github/workflows/helm.yml@refs/tags/helm-' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
```

Chart versions up to 0.5.1 were released from the
[plan4better/charts](https://github.com/plan4better/charts) repository (tags
`goat-<version>`) and are signed by its workflow: use
`--certificate-identity-regexp '^https://github.com/plan4better/charts/.github/workflows/release.yml@'`
for those.
