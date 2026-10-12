"""Models declare the support columns; the migration only adds what is missing."""

import importlib.util
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from core.db.models import (
    Organization,
    SupportTicketRead,
    User,
)

MIGRATION = (
    Path(__file__).resolve().parents[3]
    / "alembic"
    / "versions"
    / "0010_support_tickets.py"
)


def _load_migration():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("m0010", MIGRATION)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


@pytest.mark.unit
def test_models_declare_the_columns() -> None:
    assert "odoo_contact_id" in User.__table__.columns
    assert "odoo_company_id" in Organization.__table__.columns
    cols = SupportTicketRead.__table__.columns
    assert {c.name for c in cols} == {
        "user_id",
        "ticket_id",
        "last_seen_message_id",
        "updated_at",
    }
    assert {c.name for c in SupportTicketRead.__table__.primary_key} == {
        "user_id",
        "ticket_id",
    }


@pytest.mark.unit
def test_upgrade_is_guarded(monkeypatch: pytest.MonkeyPatch) -> None:
    m = _load_migration()
    assert m.revision == "0010_support_tickets"
    assert m.down_revision == "0009_legacy_constraint_parity"
    added = []
    monkeypatch.setattr(
        m.h, "add_column_if_missing", lambda t, c, s: added.append((t, c.name))
    )
    monkeypatch.setattr(m.h, "table_exists", lambda name, schema: True)
    create_table = MagicMock()
    monkeypatch.setattr(m.op, "create_table", create_table)
    m.upgrade()
    assert added == [("user", "odoo_contact_id"), ("organization", "odoo_company_id")]
    create_table.assert_not_called()  # table already there → untouched


@pytest.mark.unit
def test_downgrade_keeps_the_shared_columns(monkeypatch: pytest.MonkeyPatch) -> None:
    m = _load_migration()
    dropped_tables, dropped_cols = [], []
    monkeypatch.setattr(
        m.h, "drop_table_if_present", lambda n, s: dropped_tables.append(n)
    )
    monkeypatch.setattr(
        m.h, "drop_column_if_present", lambda *a: dropped_cols.append(a)
    )
    m.downgrade()
    assert dropped_tables == ["support_ticket_read"]
    assert dropped_cols == []
