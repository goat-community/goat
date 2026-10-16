---
name: windmill
description: Use when working with GOAT's Windmill instance — running or syncing analytics tools, inspecting job execution, adding a new tool, or checking which f/goat/tools/* scripts exist. Use the Windmill MCP tools for API calls.
---

# Windmill

Context for GOAT's Windmill instance. Use the Windmill MCP tools for API calls; this skill provides domain knowledge.

## Setup

- **URL / Web UI**: `WINDMILL_URL` in `.env` (local dev: http://localhost:8110)
- **Workspace**: `goat`
- **Token**: `WINDMILL_TOKEN` in `.env` — never hardcode it

## Folder Structure

All scripts live under `f/goat/`:
- `f/goat/tools/` — Analytics tools (synced from goatlib, run by the `processes` service)
- `f/goat/tasks/` — Background tasks (thumbnails, S3 sync, etc.)

## Tools — do not hardcode the list

The tool set changes often. The **single source of truth** is the registry:
`packages/python/goatlib/src/goatlib/tools/registry.py` (`TOOL_REGISTRY`). Scripts under
`f/goat/tools/` are auto-generated from it via `python -m goatlib.tools.sync_windmill`.

To see the current tools (grouped by category, with hidden/beta/worker flags), run from repo root:

```bash
uv run python -c "
from itertools import groupby
from goatlib.tools.registry import TOOL_REGISTRY
for cat, items in groupby(sorted(TOOL_REGISTRY, key=lambda t: t.category), key=lambda t: t.category):
    print(f'## {cat}')
    for t in items:
        flags = [f for f, on in (('hidden', t.toolbox_hidden), ('beta', t.beta), (f'worker={t.worker_tag}', t.worker_tag != 'tools')) if on]
        print(f\"  {t.windmill_path}{'  [' + ', '.join(flags) + ']' if flags else ''} — {t.description}\")
"
```

Categories: `geoprocessing`, `data_management`, `geoanalysis`, `accessibility_indicators`, `data`
(the `data` category is toolbox-hidden internal tools: layer import/update/delete/export/create,
project export/import, print report). `toolbox_hidden` tools stay callable via the API but don't
appear in the toolbox UI; `beta` tools render in a Beta sub-section; `worker_tag` routes the job to a
specific Windmill worker (e.g. `print`).

## How Tools Execute

1. Frontend calls the `processes` service API to start a tool
2. `processes` submits it to Windmill as a job (`f/goat/tools/<tool>`)
3. Windmill runs the generated Python script, which imports from `goatlib.tools`
4. The tool class (`BaseToolRunner` subclass) reads input from DuckLake, processes, writes output to DuckLake
5. The client polls `processes` (`GET /jobs/{jobId}`) for status and result; job state lives in Windmill, not in the GOAT database

## Adding / Changing a Tool

1. Add or edit the tool class in `goatlib/tools/<name>.py` (inherit `BaseToolRunner[TParams]`)
2. Register it in `goatlib/tools/registry.py` (`TOOL_REGISTRY`) — this is what makes it appear everywhere
3. Sync to Windmill (reads `WINDMILL_URL` / `WINDMILL_TOKEN` from the environment):

```bash
set -a && source .env && set +a
uv run python -m goatlib.tools.sync_windmill
```

## Checking Jobs

Via Windmill MCP, or the processes API (`GET /jobs`, `GET /jobs/{jobId}`). GOAT's own database has no job table.

## Key Code Paths

- Tool registry (source of truth): `packages/python/goatlib/src/goatlib/tools/registry.py`
- Tool base class: `packages/python/goatlib/src/goatlib/tools/base.py`
- Individual tools: `packages/python/goatlib/src/goatlib/tools/<name>.py`
- Windmill sync: `packages/python/goatlib/src/goatlib/tools/sync_windmill.py`
- Code generation: `packages/python/goatlib/src/goatlib/tools/codegen.py`
- Processes API: `apps/processes/` (OGC API Processes service)
