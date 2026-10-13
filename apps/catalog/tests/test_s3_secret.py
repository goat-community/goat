"""The catalog's S3 secret takes its SSL flag from the endpoint's scheme.

DuckDB rejects a scheme inside the endpoint, and without USE_SSL it uses TLS,
so a plain http:// endpoint (a local MinIO or Garage) failed with an SSL
error before the scheme was turned into USE_SSL.
"""

from pathlib import Path
from typing import Any

import pytest

from catalog.config import CatalogSettings
from catalog.services.s3_secret import create_s3_secret


class _RecordingConnection:
    def __init__(self) -> None:
        self.calls: list[tuple[str, list[Any]]] = []

    def execute(self, sql: str, params: list[Any]) -> None:
        self.calls.append((sql, params))


def _secret(tmp_path: Path, endpoint: str | None) -> tuple[str, list[Any]]:
    settings = CatalogSettings(
        data_dir=tmp_path,
        s3_endpoint_url=endpoint,
        s3_access_key_id="key",
        s3_secret_access_key="secret",
    )
    con = _RecordingConnection()
    create_s3_secret(con, "catalog_data", settings)  # type: ignore[arg-type]
    ((sql, params),) = con.calls
    return sql, params


@pytest.mark.parametrize(
    ("endpoint", "host", "use_ssl"),
    [
        ("http://localhost:3900", "localhost:3900", False),
        ("https://s3.example.org", "s3.example.org", True),
        ("https://s3.example.org/prefix/", "s3.example.org/prefix", True),
    ],
)
def test_the_scheme_sets_use_ssl(
    tmp_path: Path, endpoint: str, host: str, use_ssl: bool
) -> None:
    sql, params = _secret(tmp_path, endpoint)

    assert "USE_SSL ?" in sql
    assert params[2] == host
    assert params[-1] is use_ssl


def test_an_endpoint_without_scheme_keeps_duckdbs_default(tmp_path: Path) -> None:
    sql, params = _secret(tmp_path, "s3.example.org")

    assert "USE_SSL" not in sql
    assert params[2] == "s3.example.org"
