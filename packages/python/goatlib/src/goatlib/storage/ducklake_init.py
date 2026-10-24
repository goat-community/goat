"""One-shot DuckLake catalog bootstrap.

Idempotent ATTACH that creates the DuckLake catalog (Postgres metadata
schema + S3/local data layout) if missing, no-op against an existing
catalog. Intended as a pre-flight step before any read-only consumer
(geoapi, processes) starts up — DuckDB refuses to attach a non-existent
catalog in READ_ONLY mode.

Usage:
    python -m goatlib.storage.ducklake_init

Env-var contract matches the legacy `scripts/db/init-ducklake.py` so the
script in the goat monorepo can later become a thin wrapper that just
calls `bootstrap_from_env()` here, without breaking the docker-compose
`ducklake-init` service or any other consumer reading the same env vars.

Kept in a sibling module to ducklake.py (rather than appended to it)
because the long-running connection manager + pool there carry state
that's irrelevant to a zero-state one-shot bootstrap; the two pieces
have different lifecycles, different tests, different reviewers.
"""

from __future__ import annotations

import os
import re
import sys

import duckdb

from goatlib.config.postgres import (
    DUCKLAKE_INIT_APPLICATION_NAME,
    ducklake_postgres_endpoint,
)
from goatlib.storage.ducklake import (
    REQUIRED_DUCKDB_EXTENSIONS,
    catalog_libpq,
    connect_duckdb,
    load_extensions,
)
from goatlib.storage.s3_config import apply_duckdb_s3_settings, duckdb_s3_endpoint
from goatlib.utils.credentials import postgres_attach_target

# Postgres indexes DuckLake does not create itself; on a catalog of ~20k tables
# each lookup without them scans a table of 200k+ rows.
# - table_column_stats: DuckLake 1.1 (DuckDB 2.0) updates a table's global column
#   statistics one column per statement, so each feature edit took ~0.6 s
#   instead of ~0.08 s.
# - file_column_stats, data_file: a query that filters on a column reads the
#   per-file statistics of that column to skip files, ~13 ms more for every
#   filtered statistics, tile or features query on a pinned snapshot.
CATALOG_INDEXES = {
    "ducklake_table_column_stats_table_column": (
        "ducklake_table_column_stats (table_id, column_id)"
    ),
    "ducklake_file_column_stats_table_column": (
        "ducklake_file_column_stats (table_id, column_id)"
    ),
    "ducklake_data_file_table": "ducklake_data_file (table_id)",
}


def ensure_catalog_indexes(con: duckdb.DuckDBPyConnection, schema: str) -> None:
    """Create the CATALOG_INDEXES that are missing; a no-op once they exist.

    Every pod's bootstrap runs this, so it looks the indexes up first: even with
    IF NOT EXISTS, CREATE INDEX waits for a lock that blocks catalog writes. An
    index only speeds up the catalog, so one that cannot be created (a catalog
    user without the right to, a lock that times out) is reported and the
    bootstrap carries on.
    """
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", schema):
        print(f"WARNING: not indexing catalog schema {schema!r}: unusual name")
        return
    # By definition, not name: an operator's own index on the same columns counts.
    lookup = f"SELECT indexdef FROM pg_indexes WHERE schemaname = ''{schema}''"
    try:
        existing = [
            definition
            for (definition,) in con.execute(
                "SELECT indexdef FROM postgres_query("
                f"'__ducklake_metadata_lake', '{lookup}')"
            ).fetchall()
        ]
    except duckdb.Error as e:
        print(f"WARNING: could not list catalog indexes: {e}")
        return
    for name, target in CATALOG_INDEXES.items():
        table, columns = target.split(" ", 1)
        if any(f".{table} USING btree {columns}" in d for d in existing):
            continue
        try:
            con.execute(
                "CALL postgres_execute('__ducklake_metadata_lake', "
                f"'CREATE INDEX IF NOT EXISTS {name} ON \"{schema}\".{target}')"
            )
        except duckdb.Error as e:
            print(f"WARNING: could not create catalog index {name}: {e}")


def bootstrap_from_env() -> None:
    """Idempotent DuckLake catalog ATTACH driven by env vars.

    Required:
        POSTGRES_PASSWORD

    Optional (with defaults):
        POSTGRES_SERVER         (default: "db")
        DUCKLAKE_POSTGRES_SERVER (default: POSTGRES_SERVER; the host the
                                 services' DuckLake attaches use, e.g. the
                                 primary behind a transaction pooler)
        POSTGRES_PORT           (default: "5432")
        DUCKLAKE_POSTGRES_PORT  (default: POSTGRES_PORT; that host's port)
        POSTGRES_USER           (default: "postgres")
        POSTGRES_DB             (default: "goat")
        DUCKLAKE_DATA_DIR       (default: "/app/data/ducklake")
        DUCKLAKE_CATALOG_SCHEMA (default: "ducklake")

    Optional (no defaults — S3 only configured if endpoint is set):
        S3_ENDPOINT_URL         e.g. "http://minio:9000"
        S3_ACCESS_KEY_ID
        S3_SECRET_ACCESS_KEY

    Raises SystemExit(1) on missing POSTGRES_PASSWORD, otherwise prints
    progress to stdout and returns normally on success.
    """
    pg_host, pg_port = ducklake_postgres_endpoint(
        os.environ.get("POSTGRES_SERVER", "db"),
        os.environ.get("POSTGRES_PORT", "5432"),
        os.environ.get("DUCKLAKE_POSTGRES_SERVER"),
        os.environ.get("DUCKLAKE_POSTGRES_PORT"),
    )
    pg_user = os.environ.get("POSTGRES_USER", "postgres")
    pg_password = os.environ.get("POSTGRES_PASSWORD")
    pg_db = os.environ.get("POSTGRES_DB", "goat")
    storage_path = os.environ.get("DUCKLAKE_DATA_DIR", "/app/data/ducklake")
    catalog_schema = os.environ.get("DUCKLAKE_CATALOG_SCHEMA", "ducklake")
    s3_endpoint = os.environ.get("S3_ENDPOINT_URL", "")
    s3_access_key = os.environ.get("S3_ACCESS_KEY_ID", "")
    s3_secret_key = os.environ.get("S3_SECRET_ACCESS_KEY", "")

    if not pg_password:
        print("ERROR: POSTGRES_PASSWORD is required", file=sys.stderr)
        sys.exit(1)

    os.makedirs(storage_path, exist_ok=True)

    print("Initializing DuckLake...")
    print(f"  PostgreSQL: {pg_host}:{pg_port}/{pg_db}")
    print(f"  Catalog schema: {catalog_schema}")
    print(f"  Data directory: {storage_path}")

    con = connect_duckdb()

    print("Loading DuckDB extensions...")
    load_extensions(con, *REQUIRED_DUCKDB_EXTENSIONS)

    if s3_endpoint:
        print(f"  S3 endpoint: {duckdb_s3_endpoint(s3_endpoint)[0]}")
        apply_duckdb_s3_settings(
            con,
            endpoint_url=s3_endpoint,
            access_key=s3_access_key,
            secret_key=s3_secret_key,
        )

    pg_uri = catalog_libpq(
        {
            "host": pg_host,
            "port": pg_port,
            "user": pg_user,
            "password": pg_password,
            "dbname": pg_db,
        },
        DUCKLAKE_INIT_APPLICATION_NAME,
    )

    print("Attaching DuckLake catalog...")
    pg_uri = postgres_attach_target(con, pg_uri)
    # No READ_ONLY → DuckDB creates the catalog if missing, otherwise no-op.
    con.execute(
        f"ATTACH 'ducklake:postgres:{pg_uri}' AS lake ("
        f"  DATA_PATH '{storage_path}', "
        f"  METADATA_SCHEMA '{catalog_schema}'"
        f")"
    )

    ensure_catalog_indexes(con, catalog_schema)

    print("DuckLake initialized successfully!")
    print(f"  Catalog: {catalog_schema}")
    print(f"  Data path: {storage_path}")

    con.close()


if __name__ == "__main__":
    bootstrap_from_env()
