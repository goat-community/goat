"""DuckLake's catalog connections can bypass a transaction pooler.

They stay open for as long as an attach lives, so behind a pooler they go to
the database itself, whose host and often port differ from the pooler's
(PgBouncer on 6432, the database on 5432).
"""

import pytest
from goatlib.config.postgres import ducklake_postgres_endpoint
from goatlib.tools.base import ToolSettings


@pytest.mark.unit
def test_unset_uses_the_apps_own_host_and_port() -> None:
    assert ducklake_postgres_endpoint("pooler", "6432") == ("pooler", 6432)
    assert ducklake_postgres_endpoint("pooler", "6432", "", "") == ("pooler", 6432)


@pytest.mark.unit
def test_host_and_port_each_override() -> None:
    assert ducklake_postgres_endpoint("pooler", 6432, "primary", "5432") == (
        "primary",
        5432,
    )
    assert ducklake_postgres_endpoint("db", 6432, None, 5432) == ("db", 5432)


@pytest.mark.unit
def test_tool_runs_attach_through_the_direct_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("POSTGRES_SERVER", "pooler")
    monkeypatch.setenv("POSTGRES_PORT", "6432")
    monkeypatch.setenv("DUCKLAKE_POSTGRES_SERVER", "primary")
    monkeypatch.setenv("DUCKLAKE_POSTGRES_PORT", "5432")

    settings = ToolSettings.from_env()

    assert "@primary:5432/" in settings.ducklake_postgres_uri
    assert settings.postgres_server == "pooler"
    assert settings.postgres_port == 6432
