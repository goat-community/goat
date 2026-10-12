import pytest
from goatlib.config.io import IOSettings
from goatlib.tools.base import ToolSettings


def test_io_settings_ignore_empty_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAX_UPLOAD_DATASET_FILE_SIZE", "")
    assert IOSettings(_env_file=None).max_upload_dataset_file_size > 0


def test_tool_secret_empty_env_falls_back_to_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SCHEMA", "")
    assert ToolSettings._get_secret("SCHEMA", "customer") == "customer"


def test_tool_secret_set_env_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SCHEMA", "other")
    assert ToolSettings._get_secret("SCHEMA", "customer") == "other"
