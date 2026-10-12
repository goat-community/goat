# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GOAT is an open-source WebGIS platform for integrated planning, built as a monorepo with a FastAPI/Python backend and React/Next.js/TypeScript frontend. It provides GIS tools, geospatial data management, and accessibility analyses.

**Key architectural separation**: Layer metadata lives in PostgreSQL (managed by `core`), layer data lives in DuckLake (managed by `geoapi`). The `processes` service is separated from `geoapi` to prevent long-running analytics jobs from blocking tile/feature requests.

The `catalog` service is database-less: it serves a local parquet mirror under `${DATA_DIR}/catalog`, kept current by the goatlib `sync_catalog` task; catalog items are promoted into `customer.layer` on first use. Its design decisions and the harvester contract are in `apps/catalog/README.md`.

Docs-writing rules and diagram exports live in `apps/docs/CLAUDE.md`; adding or syncing an analytics tool is covered by the `windmill` skill.

## Gotchas

- Sync Python with `uv sync --all-packages`: a plain `uv sync` prunes the workspace members' dependencies.
- `AUTH=False` is the single switch that disables auth for the backend, the web middleware and the client bundle.

## Releases

- `deploy/compose` — single-server Docker Compose bundle, released as `goat-compose-<tag>.tar.gz` on every `v*` tag; tests in `deploy/compose/tests/`
- `deploy/helm/goat` — Helm chart, own version in `Chart.yaml`, released to `oci://ghcr.io/plan4better/charts/goat` on `helm-<version>` tags (`.github/workflows/helm.yml`, no GitHub release); `deploy/helm/check.sh` runs lint + unit tests + renders

## Deployment Targets Follow Every Change

- **MUST: a change to anything a deployment sees updates every place GOAT is deployed from, in the same change.** That covers a new, renamed or removed setting or environment variable, a changed default, a new service, job, port, volume, secret or image, and changed URL or auth wiring. Update all of:
  - `deploy/compose`: `.env.example` (with a comment), `compose.yaml`, `setup.sh` when it derives the value, `tests/`, the bundle README;
  - `deploy/helm/goat`: `values.yaml`, `values.schema.json`, templates, unit tests in `tests/`, the chart README (values table and version history); `deploy/helm/check.sh` must pass;
  - the Kubernetes overlays of Plan4Better's own dev and prod clusters (separate infra repository);
  - the self-hosting docs in `apps/docs`, English and German.
- Before calling such a change done, grep the setting's name across `deploy/` and `apps/docs/` and account for every target: updated, or not applicable and why.

## Service READMEs Follow Every Change

- **MUST: a change to a service's purpose, design decisions, storage model, access rules or the gotchas its README lists updates that README in the same change** (`apps/{core,geoapi,processes,catalog}/README.md`, `packages/python/goatlib/README.md`). READMEs hold the "why" and point to the sources of truth (registries, `config.py`, `/api/docs`) instead of copying lists of tools, settings or routes; keep it that way.
- The `doc-references` PR check (`scripts/check-doc-references.py`) fails when a README or CLAUDE.md names a file or setting that no longer exists. Run it locally after renaming or removing either.

## Commit Convention

Uses conventional commits (commitlint + commitizen + husky). Format: `type(scope): description`.
