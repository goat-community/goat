"""core reads the repo-wide AUTH flag and refuses to start without Keycloak.

The module-level ``settings`` is built at import, so these tests construct
the ``Settings`` class directly.
"""

import pytest
from core.core.config import Settings

ON = ["true", "True", "1", "yes", "on", ""]
OFF = ["false", "False", "0", "no", "off"]


@pytest.fixture(autouse=True)
def _env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AUTH", raising=False)
    monkeypatch.delenv("KEYCLOAK_SERVER_URL", raising=False)
    monkeypatch.setenv("POSTGRES_SERVER", "localhost")
    monkeypatch.setenv("POSTGRES_USER", "goat")
    monkeypatch.setenv("POSTGRES_PASSWORD", "goat")
    monkeypatch.setenv("POSTGRES_DB", "goat")


@pytest.mark.parametrize("raw", ON)
def test_auth_on_spellings(monkeypatch: pytest.MonkeyPatch, raw: str) -> None:
    monkeypatch.setenv("AUTH", raw)
    monkeypatch.setenv("KEYCLOAK_SERVER_URL", "http://kc")
    assert Settings().AUTH is True


@pytest.mark.parametrize("raw", OFF)
def test_auth_off_spellings(monkeypatch: pytest.MonkeyPatch, raw: str) -> None:
    monkeypatch.setenv("AUTH", raw)
    assert Settings().AUTH is False


def test_auth_on_without_keycloak_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTH", "true")
    with pytest.raises(ValueError, match="KEYCLOAK_SERVER_URL"):
        Settings()


def test_no_keycloak_host_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTH", "false")
    assert not Settings().KEYCLOAK_SERVER_URL
