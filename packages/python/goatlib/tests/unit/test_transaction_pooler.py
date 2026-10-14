"""GOAT works behind a connection pooler in transaction mode.

There each query may run on another server connection, and a pooler with
stock settings neither keeps track of prepared statements nor passes on
startup parameters it doesn't know. POSTGRES_TRANSACTION_POOLER turns off
asyncpg's statement cache and the keepalive settings for every connection.
"""

import pytest
from goatlib.config.postgres import (
    KEEPALIVE_SERVER_SETTINGS,
    asyncpg_connect_args,
    parse_transaction_pooler,
    transaction_pooler_enabled,
)
from goatlib.tools.base import ToolSettings


@pytest.mark.unit
@pytest.mark.parametrize(
    ("value", "enabled"),
    [("true", True), ("1", True), (" On ", True), ("false", False), ("", False)],
)
def test_the_switch_reads_the_usual_spellings(value: str, enabled: bool) -> None:
    assert transaction_pooler_enabled(lambda name, default="": value) is enabled


@pytest.mark.unit
@pytest.mark.parametrize(
    ("value", "enabled"),
    [(True, True), (False, False), (None, False), ("", False), (" TRUE ", True)],
)
def test_any_value_parses_without_error(value: object, enabled: bool) -> None:
    assert parse_transaction_pooler(value) is enabled


@pytest.mark.unit
def test_direct_connections_keep_the_cache_and_keepalives() -> None:
    args = asyncpg_connect_args("goat-geoapi", False, keepalives=True)
    assert "statement_cache_size" not in args
    assert args["server_settings"] == {
        "application_name": "goat-geoapi",
        **KEEPALIVE_SERVER_SETTINGS,
    }


@pytest.mark.unit
def test_behind_a_pooler_nothing_is_cached_and_only_the_name_is_sent() -> None:
    args = asyncpg_connect_args("goat-geoapi", True, keepalives=True)
    assert args["statement_cache_size"] == 0
    assert args["server_settings"] == {"application_name": "goat-geoapi"}


@pytest.mark.unit
def test_tool_and_task_connections_follow_the_switch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("POSTGRES_TRANSACTION_POOLER", "true")
    assert ToolSettings.from_env().postgres_connect_args()["statement_cache_size"] == 0

    monkeypatch.delenv("POSTGRES_TRANSACTION_POOLER")
    assert "statement_cache_size" not in ToolSettings.from_env().postgres_connect_args()
