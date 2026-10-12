"""The catalog reads the repo-wide AUTH flag and refuses to start without Keycloak."""

import pytest

from catalog.config import CatalogSettings

ON = ["true", "True", "1", "yes", "on", ""]
OFF = ["false", "False", "0", "no", "off"]


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "AUTH",
        "CATALOG_AUTH",
        "KEYCLOAK_SERVER_URL",
        "CATALOG_KEYCLOAK_SERVER_URL",
    ):
        monkeypatch.delenv(name, raising=False)


@pytest.mark.parametrize("raw", ON)
def test_auth_on_spellings(monkeypatch: pytest.MonkeyPatch, raw: str) -> None:
    monkeypatch.setenv("AUTH", raw)
    monkeypatch.setenv("KEYCLOAK_SERVER_URL", "http://kc")
    assert CatalogSettings().auth is True


@pytest.mark.parametrize("raw", OFF)
def test_auth_off_spellings(monkeypatch: pytest.MonkeyPatch, raw: str) -> None:
    monkeypatch.setenv("AUTH", raw)
    assert CatalogSettings().auth is False


def test_auth_on_without_keycloak_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTH", "true")
    with pytest.raises(ValueError, match="KEYCLOAK_SERVER_URL"):
        CatalogSettings()


def test_no_plan4better_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTH", "false")
    assert "plan4better" not in CatalogSettings().keycloak_server_url
