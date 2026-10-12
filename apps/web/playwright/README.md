# End-to-end tests

Playwright specs that drive the real app in a browser: content management,
project creation, the dataset picker, templates, workflows, Home. The config
is `playwright.config.ts` at the repo root.

## Where they run

- **CI:** `.github/workflows/e2e.yml`, on every PR that changes the app, a
  service or the suite, on every push to `main`, and on demand ("Run
  workflow" in the Actions tab). It starts Postgres and Redis from
  the root `compose.yaml`, Garage for S3, core, geoapi, processes and catalog
  from source, and a production build of the web app, all with `AUTH=False`. A
  failed run uploads the Playwright report and every service's log as the
  `e2e-report` artifact. It is not a required check yet.
- **Locally:** against a running app on port 3000, for example
  `pnpm exec playwright test --config=playwright.config.ts` from the repo
  root (pass the config explicitly when running from a worktree).

## What the specs assume

- `AUTH=False`: every request is the built-in default user (first name
  "GOAT"), so nothing logs in.
- Two datasets owned by that user, one of them a feature layer. A fresh
  database gets them from `python -m core.scripts.seed_e2e` (in `apps/core`,
  after `initial_data`); the CI stack does not run Windmill, so they cannot be
  created through the app.
- The specs create what else they need (projects, folders, the shared team
  "Design QA") and remove it again, except the team, which stays on purpose.

## Not covered

Anything that needs Windmill: dataset imports, tool runs, workflow runs,
thumbnails, printing. The upload specs only check that the upload dialog
submits.
