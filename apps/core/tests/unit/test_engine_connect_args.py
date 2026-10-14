"""core's engines behind a connection pooler in transaction mode.

psycopg prepares a statement on the server once it ran a few times on a
connection; behind such a pooler the next query may land on a server
connection where that statement is missing or already taken. With
POSTGRES_TRANSACTION_POOLER psycopg prepares nothing. SQLAlchemy's asyncpg
dialect prepares every statement in a round trip of its own, so it is refused
there.
"""

import pytest
from core.core.config import settings
from core.db.session import engine_connect_args

PSYCOPG = "postgresql+psycopg://u:p@pooler:6432/goat"
ASYNCPG = "postgresql+asyncpg://u:p@pooler:6432/goat"


def test_psycopg_prepares_as_usual_by_default(monkeypatch) -> None:
    monkeypatch.setattr(settings, "POSTGRES_TRANSACTION_POOLER", False)
    assert engine_connect_args(PSYCOPG) == {"application_name": "goat-core"}


def test_psycopg_prepares_nothing_behind_a_pooler(monkeypatch) -> None:
    monkeypatch.setattr(settings, "POSTGRES_TRANSACTION_POOLER", True)
    assert engine_connect_args(PSYCOPG) == {
        "application_name": "goat-core",
        "prepare_threshold": None,
    }


def test_asyncpg_is_refused_behind_a_pooler(monkeypatch) -> None:
    monkeypatch.setattr(settings, "POSTGRES_TRANSACTION_POOLER", False)
    assert engine_connect_args(ASYNCPG) == {
        "server_settings": {"application_name": "goat-core"}
    }
    monkeypatch.setattr(settings, "POSTGRES_TRANSACTION_POOLER", True)
    with pytest.raises(ValueError, match="psycopg"):
        engine_connect_args(ASYNCPG)


@pytest.mark.parametrize(("value", "enabled"), [("", False), (" on ", True)])
def test_any_spelling_starts_core(monkeypatch, value: str, enabled: bool) -> None:
    """A blank or padded value must not stop core from starting."""
    from core.core.config import Settings

    monkeypatch.setenv("POSTGRES_TRANSACTION_POOLER", value)
    assert Settings().POSTGRES_TRANSACTION_POOLER is enabled
