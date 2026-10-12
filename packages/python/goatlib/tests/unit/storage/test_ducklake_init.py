"""The DuckLake bootstrap attaches through the same host as the services.

geoapi, processes and the tools connect their DuckLake attaches to
DUCKLAKE_POSTGRES_SERVER when it is set (straight to Postgres, past a
transaction pooler that POSTGRES_SERVER may point at). The bootstrap that
creates the catalog must use that host too.
"""

from typing import Any

import pytest
from goatlib.storage import ducklake_init


class _RecordingConnection:
    def __init__(self) -> None:
        self.executed: list[str] = []

    def execute(self, sql: str, *_: Any) -> "_RecordingConnection":
        self.executed.append(sql)
        return self

    def close(self) -> None:
        pass


@pytest.fixture
def connection(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> _RecordingConnection:
    con = _RecordingConnection()
    monkeypatch.setattr(ducklake_init.duckdb, "connect", lambda: con)
    monkeypatch.setenv("DUCKDB_EXTENSION_DIRECTORY", str(tmp_path / "extensions"))
    for name in ("S3_ENDPOINT_URL", "DUCKLAKE_POSTGRES_SERVER"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("POSTGRES_SERVER", "pooler")
    monkeypatch.setenv("POSTGRES_PASSWORD", "secret")
    monkeypatch.setenv("DUCKLAKE_DATA_DIR", str(tmp_path / "ducklake"))
    return con


def _attach(con: _RecordingConnection) -> str:
    (sql,) = [s for s in con.executed if s.startswith("ATTACH")]
    return sql


@pytest.mark.unit
def test_the_catalog_is_attached_through_the_direct_host_when_set(
    connection: _RecordingConnection, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DUCKLAKE_POSTGRES_SERVER", "primary")

    ducklake_init.bootstrap_from_env()

    assert "host=primary " in _attach(connection)


@pytest.mark.unit
def test_without_a_direct_host_the_catalog_uses_postgres_server(
    connection: _RecordingConnection,
) -> None:
    ducklake_init.bootstrap_from_env()

    assert "host=pooler " in _attach(connection)


@pytest.mark.unit
def test_the_bootstrap_session_is_named_and_loads_baked_extensions(
    connection: _RecordingConnection,
) -> None:
    ducklake_init.bootstrap_from_env()

    assert "application_name=goat-ducklake-init" in _attach(connection)
    assert not [sql for sql in connection.executed if sql.startswith("INSTALL")]
