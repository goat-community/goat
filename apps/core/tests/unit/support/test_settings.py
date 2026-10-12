"""The support feature is on only when all four Odoo settings are present."""

import pytest
from core.core.config import settings
from core.support.deps import require_support_enabled
from fastapi import HTTPException


@pytest.fixture
def _all_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "ODOO_URL", "https://odoo.example")
    monkeypatch.setattr(settings, "ODOO_DB", "db")
    monkeypatch.setattr(settings, "ODOO_SUPPORT_API_KEY", "key")
    monkeypatch.setattr(settings, "ODOO_SUPPORT_TEAM_ID", 1)


@pytest.mark.unit
def test_enabled_when_all_four_are_set(_all_set: None) -> None:
    assert settings.support_enabled is True
    require_support_enabled()  # does not raise


@pytest.mark.unit
@pytest.mark.parametrize(
    "name",
    [
        "ODOO_URL",
        "ODOO_DB",
        "ODOO_SUPPORT_API_KEY",
        "ODOO_SUPPORT_TEAM_ID",
    ],
)
def test_disabled_when_one_is_missing(
    _all_set: None, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    monkeypatch.setattr(settings, name, None)
    assert settings.support_enabled is False
    with pytest.raises(HTTPException) as exc:
        require_support_enabled()
    assert exc.value.status_code == 404


@pytest.mark.unit
def test_defaults() -> None:
    assert (
        settings.ODOO_SUPPORT_POST_ACTION == "GOAT: post message as ticket participant"
    )
