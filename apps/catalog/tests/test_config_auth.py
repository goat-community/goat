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
        "AUTH_ALLOWED_CLIENTS",
        "CATALOG_AUTH_ALLOWED_CLIENTS",
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


def test_allowed_clients_default_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTH", "false")
    assert CatalogSettings().auth_allowed_clients == ""


def test_allowed_clients_reads_the_bare_name(monkeypatch: pytest.MonkeyPatch) -> None:
    """One name for every service: the CATALOG_ prefix does not apply."""
    monkeypatch.setenv("AUTH", "false")
    monkeypatch.setenv("AUTH_ALLOWED_CLIENTS", "goat-web,goat-scripts")
    assert CatalogSettings().auth_allowed_clients == "goat-web,goat-scripts"


def test_token_check_uses_the_allowed_clients(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The catalog's KeycloakAuth gets the setting; goatlib enforces it."""
    from catalog.auth import _get_keycloak_auth

    monkeypatch.setenv("KEYCLOAK_SERVER_URL", "http://kc")
    monkeypatch.setenv("AUTH_ALLOWED_CLIENTS", "goat-web, goat-scripts")
    auth = _get_keycloak_auth(CatalogSettings())
    assert auth.allowed_clients == frozenset({"goat-web", "goat-scripts"})
    monkeypatch.setenv("AUTH_ALLOWED_CLIENTS", "")
    assert not _get_keycloak_auth(CatalogSettings()).allowed_clients
