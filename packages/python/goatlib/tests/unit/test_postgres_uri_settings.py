"""The tools' DuckLake URI keeps any password intact."""

import pytest
from goatlib.tools.base import ToolSettings
from goatlib.utils.credentials import without_password

PASSWORD = '$t3st!PW""x Y09?a@b#c%d/e:f$$2026$$\''


@pytest.mark.parametrize("direct", [None, "primary"])
def test_the_ducklake_uri_keeps_any_password_intact(
    monkeypatch: pytest.MonkeyPatch, direct: str | None
) -> None:
    monkeypatch.delenv("POSTGRES_DATABASE_URI", raising=False)
    monkeypatch.setenv("POSTGRES_SERVER", "db")
    monkeypatch.setenv("POSTGRES_PASSWORD", PASSWORD)
    if direct:
        monkeypatch.setenv("DUCKLAKE_POSTGRES_SERVER", direct)
    else:
        monkeypatch.delenv("DUCKLAKE_POSTGRES_SERVER", raising=False)
        monkeypatch.delenv("DUCKLAKE_POSTGRES_PORT", raising=False)

    target, password = without_password(ToolSettings.from_env().ducklake_postgres_uri)

    assert password == PASSWORD
    assert f"host={direct or 'db'} " in target
