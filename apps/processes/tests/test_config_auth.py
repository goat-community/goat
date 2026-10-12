"""processes reads the repo-wide AUTH flag and refuses to start without Keycloak.

The module-level ``settings`` is built at import, so these tests construct
the ``Settings`` class directly, without the ``.env`` file.
"""

import pytest

from processes.config import Settings

ON = ["true", "True", "1", "yes", "on", ""]
OFF = ["false", "False", "0", "no", "off"]


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("AUTH", "KEYCLOAK_SERVER_URL", "REALM_NAME"):
        monkeypatch.delenv(name, raising=False)


def _settings() -> Settings:
    return Settings(_env_file=None)


@pytest.mark.parametrize("raw", ON)
def test_auth_on_spellings(monkeypatch: pytest.MonkeyPatch, raw: str) -> None:
    monkeypatch.setenv("AUTH", raw)
    monkeypatch.setenv("KEYCLOAK_SERVER_URL", "http://kc")
    assert _settings().AUTH is True


@pytest.mark.parametrize("raw", OFF)
def test_auth_off_spellings(monkeypatch: pytest.MonkeyPatch, raw: str) -> None:
    monkeypatch.setenv("AUTH", raw)
    assert _settings().AUTH is False


def test_auth_unset_is_on(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KEYCLOAK_SERVER_URL", "http://kc")
    assert _settings().AUTH is True


def test_auth_on_without_keycloak_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTH", "true")
    with pytest.raises(ValueError, match="KEYCLOAK_SERVER_URL"):
        _settings()


def test_no_plan4better_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTH", "false")
    assert "plan4better" not in _settings().KEYCLOAK_SERVER_URL


def test_keycloak_reads_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KEYCLOAK_SERVER_URL", "http://kc")
    monkeypatch.setenv("REALM_NAME", "goat")
    s = _settings()
    assert s.KEYCLOAK_SERVER_URL == "http://kc"
    assert s.REALM_NAME == "goat"
