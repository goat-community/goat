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

## Field config and generated fields

A layer's `field_config` (in core's `customer.layer`) says what each column
means beyond its storage type: its kind, vocabulary, default, formatting or
formula. Two writers produce entries — geoapi when a column is added, and the
`layer_create` tool when a layer is declared with its columns — so the rules for
an entry live here, in `utils/field_config.py` and `utils/generated_fields.py`.

The generated kinds, `serial` (a running number, BIGINT) and `uuid` (UUID v4 as
text), are filled by whoever inserts a row, never by the user. Their settings
sit flat in the entry next to `kind` (`{"kind": "serial", "start": 1}`), so
later variants — a display `format` such as `V-{0000}`, a yearly `reset`, a
UUID `version` — are further settings, not a migration. Those variants are not
implemented yet; the module docstring describes how each would fit.

A serial number is never handed out twice: the writer counts from the larger of
the table's maximum and the column's high-water mark (core's
`layer_serial_counter`, read and advanced by geoapi under its per-layer lock).
`layer_create_filtered` copies the source's marks along with its
`field_config`; a copy made any other way (project export and import) has no
mark and continues from its own highest number.

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
