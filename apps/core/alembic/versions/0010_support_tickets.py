"""Support tickets: Odoo identity columns and read markers.

`user.odoo_contact_id` and `organization.odoo_company_id` already exist,
empty and created outside any migration, on databases that ran the unmerged
Odoo billing work (Majk's local `goat`, the dev cluster). Production and
fresh databases do not have them. Every step checks the catalog first.

Downgrade drops only `support_ticket_read`: the two columns are shared with
the billing integration, and dropping them would take its data along.

Revision ID: 0010_support_tickets
Revises: 0009_legacy_constraint_parity
"""

import sys
from pathlib import Path

import sqlalchemy as sa
from alembic import op
from core.core.config import settings
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as UUID_PG

_ALEMBIC_DIR = str(Path(__file__).resolve().parents[1])
if _ALEMBIC_DIR not in sys.path:
    sys.path.append(_ALEMBIC_DIR)

import helpers as h  # noqa: E402

revision = "0010_support_tickets"
down_revision = "0009_legacy_constraint_parity"
branch_labels = None
depends_on = None

S = settings.SCHEMA


def upgrade() -> None:
    h.add_column_if_missing(
        "user", sa.Column("odoo_contact_id", sa.Integer(), nullable=True), S
    )
    h.add_column_if_missing(
        "organization", sa.Column("odoo_company_id", sa.Integer(), nullable=True), S
    )
    if not h.table_exists("support_ticket_read", S):
        op.create_table(
            "support_ticket_read",
            sa.Column(
                "user_id",
                UUID_PG(as_uuid=True),
                sa.ForeignKey(f"{S}.user.id", ondelete="CASCADE"),
                primary_key=True,
                nullable=False,
            ),
            sa.Column("ticket_id", sa.BigInteger(), primary_key=True, nullable=False),
            sa.Column("last_seen_message_id", sa.BigInteger(), nullable=False),
            sa.Column(
                "updated_at",
                TIMESTAMP(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
            schema=S,
        )


def downgrade() -> None:
    h.drop_table_if_present("support_ticket_read", S)
