# goatlib

Shared Python library for the GOAT platform. It contains the analytics tools,
analysis algorithms, geospatial I/O, and shared models used by the `core`,
`geoapi`, `processes`, and `catalog` services.

## Package layout

| Module | Purpose |
|--------|---------|
| `tools/` | Analytics tools (buffer, clip, catchment areas, heatmaps, …). Each tool is a `BaseToolRunner[TParams]` subclass, registered in `tools/registry.py` and executed as a Windmill job. |
| `analysis/` | Analysis algorithms backing the tools |
| `io/` | Dataset import/export, format conversion, and remote sources (WFS, …) |
| `models/` | Pydantic models shared across services |
| `services/`, `storage/`, `tasks/` | Service clients, object storage, background task helpers |
| `computed_columns/`, `i18n/`, `config/`, `utils/` | Supporting modules |

## Adding an analytics tool

1. Create the tool in `src/goatlib/tools/your_tool.py`:
   - inherit from `BaseToolRunner[YourToolParams]`
   - define the input parameters as a Pydantic model extending `ToolInputBase`
   - implement `process()` and set `tool_class`, `output_geometry_type`,
     `default_output_name`
2. Register it in `tools/registry.py`
3. Sync it to Windmill with `tools/sync_windmill.py`

Tools run with service credentials and never check the caller themselves:
the `processes` service checks every layer, project, folder and bundle a
request names before it submits the job (`apps/processes/README.md`). A new
input that names a layer needs `widget="layer-selector"` or an entry in that
check. SQL a user writes goes through `validate_sql_query` /
`validate_sql_expression` in `utils/sql_validation.py`, which allow the declared
input aliases only.

## Copies behind a project entry

Two tools replace the layer a `layer_project` entry shows instead of adding a
new entry: a workflow re-run that must not change a copied project
(`tools/workflow_export_target.py`), and `layer_copy`, which gives a template
user their own editable copy of a dataset (`tools/layer_copy.py`). Keeping the
entry is the point: dashboards, layouts, filters and workflow dataset nodes
name the entry (`layer_project_id`), so they follow the swap without being
rewritten; only the nodes' saved `layerId` is retargeted
(`tools/workflow_dataset_nodes.py`). Nodes saved with a `layerId` but no
entry (common in older projects) are retargeted by layer, and given the entry,
but only while no other entry of the project still shows the old layer: such a
node could mean that one. `layer_copy` copies DuckLake table to
table rather than through parquet, so an empty copy keeps its GEOMETRY column
(DuckDB writes no GeoParquet metadata for an empty table); it is idempotent
(an advisory lock per project and source, and a `template_copy` stamp on the
copy and its entries), and a failed run leaves the entries on the source.

## Development

The repo is a uv workspace — sync everything from the repo root:

```bash
uv sync --all-packages
```

Run the tests from this directory:

```bash
uv run pytest tests/unit         # unit tests (run in CI, advisory)
uv run pytest tests/integration  # needs local infra (DB, Garage, …)
```

## GDAL dependency

`goatlib` depends on the `gdal` Python bindings, which are distributed as an
sdist and compile against the system GDAL library — `libgdal-dev` (apt) or
equivalent must be installed to build them. Only the WFS and converter paths
in `io/` import `osgeo`, and they do so lazily, so the other services install
the workspace with `--no-install-package gdal` in CI and skip the system
dependency entirely.
