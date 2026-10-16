"""The Postgres URIs in the settings keep any password intact."""

import pytest
from goatlib.utils.credentials import without_password

from processes.config import Settings

PASSWORD = '$t3st!PW""x Y09?a@b#c%d/e:f$$2026$$\''


def test_the_uris_keep_any_password_intact(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTH", "false")
    monkeypatch.setenv("POSTGRES_SERVER", "db")
    monkeypatch.setenv("POSTGRES_PASSWORD", PASSWORD)
    settings = Settings(_env_file=None)

    for uri in (
        settings.POSTGRES_DATABASE_URI,
        settings.DUCKLAKE_POSTGRES_DATABASE_URI,
    ):
        target, password = without_password(uri)
        assert password == PASSWORD
        assert "host=" in target
