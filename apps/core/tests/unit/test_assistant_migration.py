"""Migration 0012 on a database without the assistant schema creates every
column the assistant's models define, so an upgraded database matches a fresh
one (built by ``init`` from the models)."""

import importlib.util
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import core.db.models.assistant  # noqa: F401  (registers the assistant tables)
import pytest
import sqlalchemy as sa
from core.core.config import settings
from sqlmodel import SQLModel

pytestmark = pytest.mark.unit

MIGRATION = (
    Path(__file__).resolve().parents[2] / "alembic" / "versions" / "0012_assistant.py"
)


def _created_tables() -> dict[str, set[str]]:
    spec = importlib.util.spec_from_file_location("m0012", MIGRATION)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    tables: dict[str, set[str]] = {}

    def create_table(name: str, *items: Any, **_: Any) -> None:
        tables[name] = {i.name for i in items if isinstance(i, sa.Column)}

    module.op = SimpleNamespace(execute=lambda *_: None, create_table=create_table)
    module.h = SimpleNamespace(
        table_exists=lambda *_: False, create_index_if_missing=lambda *_, **__: None
    )
    module.upgrade()
    return tables


def test_the_upgrade_creates_every_column_of_the_assistant_models() -> None:
    created = _created_tables()
    models = {
        table.name: {c.name for c in table.columns}
        for table in SQLModel.metadata.tables.values()
        if table.schema == settings.ASSISTANT_SCHEMA
    }
    assert models, "no assistant models registered"
    assert created == models
