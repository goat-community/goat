"""The DuckDB secret the catalog's S3 reads (previews, assets) sign with."""

import duckdb
from goatlib.storage.s3_config import duckdb_s3_endpoint

from catalog.config import CatalogSettings


def create_s3_secret(
    con: duckdb.DuckDBPyConnection, name: str, settings: CatalogSettings
) -> None:
    """Create the secret ``name`` for the catalog bucket on ``con``.

    DuckDB takes the endpoint without its scheme; the scheme decides
    ``USE_SSL``, so a plain ``http://`` endpoint (a local MinIO or Garage) is
    read over http. Without a scheme DuckDB's default, TLS, applies.
    """
    host, use_ssl = duckdb_s3_endpoint(settings.s3_endpoint_url or "")
    options = "TYPE s3, KEY_ID ?, SECRET ?, ENDPOINT ?, REGION ?, URL_STYLE 'path'"
    params: list[object] = [
        settings.s3_access_key_id,
        settings.s3_secret_access_key,
        host,
        settings.s3_region,
    ]
    if use_ssl is not None:
        options += ", USE_SSL ?"
        params.append(use_ssl)
    con.execute(f"CREATE OR REPLACE SECRET {name} ({options})", params)
