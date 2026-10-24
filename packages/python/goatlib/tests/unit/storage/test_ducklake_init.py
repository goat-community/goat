"""The DuckLake bootstrap attaches through the same host as the services.

geoapi, processes and the tools connect their DuckLake attaches to
DUCKLAKE_POSTGRES_SERVER when it is set (straight to Postgres, past a
transaction pooler that POSTGRES_SERVER may point at). The bootstrap that
creates the catalog must use that host too.
"""

from typing import Any

import duckdb
import pytest
from goatlib.storage import ducklake_init


class _RecordingConnection:
    def __init__(self) -> None:
        self.executed: list[str] = []
        self.indexes: list[str] = []

    def execute(self, sql: str, *_: Any) -> "_RecordingConnection":
        self.executed.append(sql)
        return self

    def fetchall(self) -> list[tuple[str]]:
        # Only the catalog index lookup reads rows here.
        return [(name,) for name in self.indexes]

    def close(self) -> None:
        pass


@pytest.fixture
def connection(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> _RecordingConnection:
    con = _RecordingConnection()
    monkeypatch.setattr(ducklake_init, "connect_duckdb", lambda: con)
    monkeypatch.setenv("DUCKDB_EXTENSION_DIRECTORY", str(tmp_path / "extensions"))
    for name in (
        "S3_ENDPOINT_URL",
        "DUCKLAKE_POSTGRES_SERVER",
        "DUCKLAKE_POSTGRES_PORT",
        "POSTGRES_PORT",
    ):
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


@pytest.mark.unit
def test_the_catalog_uses_the_direct_port_when_set(
    connection: _RecordingConnection, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("POSTGRES_PORT", "6432")
    monkeypatch.setenv("DUCKLAKE_POSTGRES_SERVER", "primary")
    monkeypatch.setenv("DUCKLAKE_POSTGRES_PORT", "5432")

    ducklake_init.bootstrap_from_env()

    assert "host=primary port=5432 " in _attach(connection)


@pytest.mark.unit
def test_the_bootstrap_indexes_the_column_stats_after_attaching(
    connection: _RecordingConnection,
) -> None:
    ducklake_init.bootstrap_from_env()

    attach = connection.executed.index(_attach(connection))
    indexes = [
        s for s in connection.executed[attach:] if "CREATE INDEX IF NOT EXISTS" in s
    ]
    for target in (
        '"ducklake".ducklake_table_column_stats (table_id, column_id)',
        '"ducklake".ducklake_file_column_stats (table_id, column_id)',
        '"ducklake".ducklake_data_file (table_id)',
    ):
        assert any(target in s for s in indexes), target


@pytest.mark.unit
def test_an_index_that_cannot_be_created_does_not_stop_the_bootstrap(
    connection: _RecordingConnection,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    record = connection.execute

    def execute(sql: str, *args: Any) -> _RecordingConnection:
        if "CREATE INDEX" in sql:
            raise duckdb.Error(
                "permission denied for table ducklake_table_column_stats"
            )
        return record(sql, *args)

    monkeypatch.setattr(connection, "execute", execute)

    ducklake_init.bootstrap_from_env()

    out = capsys.readouterr().out
    assert "could not create catalog index" in out
    assert "DuckLake initialized successfully!" in out


@pytest.mark.unit
def test_an_index_that_exists_is_not_created_again(
    connection: _RecordingConnection,
) -> None:
    """CREATE INDEX IF NOT EXISTS still waits for a lock that blocks writes."""
    connection.indexes = [
        "CREATE INDEX own_name ON ducklake.ducklake_table_column_stats "
        "USING btree (table_id, column_id)"
    ]

    ducklake_init.bootstrap_from_env()

    created = [s for s in connection.executed if "CREATE INDEX" in s]
    assert not [s for s in created if "ducklake_table_column_stats (" in s]
    assert [s for s in created if "ducklake_file_column_stats (" in s]
