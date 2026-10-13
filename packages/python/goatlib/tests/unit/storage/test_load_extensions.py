"""DuckDB extensions come from the image when it bakes them, never the network.

Images bake their extensions into DUCKDB_EXTENSION_DIRECTORY and run where
extensions.duckdb.org may be unreachable, so a connection there only loads
them. Without a baked directory (local development) they are installed first.
"""

from typing import Any

import pytest
from goatlib.storage.ducklake import load_extensions


class _RecordingConnection:
    def __init__(self) -> None:
        self.executed: list[str] = []

    def execute(self, sql: str, *_: Any) -> "_RecordingConnection":
        self.executed.append(sql)
        return self


@pytest.mark.unit
def test_baked_extensions_are_only_loaded(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DUCKDB_EXTENSION_DIRECTORY", "/opt/duckdb-extensions")
    con = _RecordingConnection()

    load_extensions(con, "spatial", "httpfs")

    assert not [sql for sql in con.executed if sql.startswith("INSTALL")]
    assert "LOAD spatial" in con.executed and "LOAD httpfs" in con.executed


@pytest.mark.unit
def test_without_a_baked_directory_extensions_are_installed_first(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DUCKDB_EXTENSION_DIRECTORY", raising=False)
    con = _RecordingConnection()

    load_extensions(con, "httpfs", "spatial")

    # All installed before any is loaded: a loaded httpfs would carry the
    # later downloads through its own TLS stack.
    assert con.executed == [
        "INSTALL httpfs",
        "INSTALL spatial",
        "LOAD httpfs",
        "LOAD spatial",
    ]
