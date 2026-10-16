"""core's database URI keeps any password intact."""

import pytest
from core.core.config import Settings
from sqlalchemy.engine import make_url

PASSWORD = '$t3st!PW""x Y09?a@b#c%d/e:f$$2026$$\''


def test_the_database_uri_keeps_any_password_intact(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ASYNC_SQLALCHEMY_DATABASE_URI", raising=False)
    monkeypatch.setenv("POSTGRES_SERVER", "db")
    monkeypatch.setenv("POSTGRES_PASSWORD", PASSWORD)

    url = make_url(Settings().ASYNC_SQLALCHEMY_DATABASE_URI)

    assert url.password == PASSWORD
    assert url.host == "db"
