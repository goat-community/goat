"""The Postgres URIs in the settings keep any password intact."""

import pytest
from goatlib.utils.credentials import without_password

from geoapi.config import Settings

PASSWORD = '$t3st!PW""x Y09?a@b#c%d/e:f$$2026$$\''


def test_the_uris_keep_any_password_intact(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTH", "false")
    settings = Settings(POSTGRES_SERVER="db", POSTGRES_PASSWORD=PASSWORD)

    for uri in (
        settings.POSTGRES_DATABASE_URI,
        settings.DUCKLAKE_POSTGRES_DATABASE_URI,
    ):
        target, password = without_password(uri)
        assert password == PASSWORD
        assert "host=" in target
