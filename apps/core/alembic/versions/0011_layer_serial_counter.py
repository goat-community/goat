"""Layer serial counters: the high-water mark of each serial column.

A serial column's next number is one past the larger of this mark and the
highest number still in the layer, so a number is never handed out again after
the feature holding it is deleted. geoapi writes the rows; the foreign key
removes them when their layer is purged.

A fresh database gets the table from the model (``init``), so the step checks
the catalog first, like every revision since the squashed baseline.

Revision ID: 0011_layer_serial_counter
Revises: 0010_support_tickets
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

revision = "0011_layer_serial_counter"
down_revision = "0010_support_tickets"
branch_labels = None
depends_on = None

S = settings.SCHEMA


def upgrade() -> None:
    if h.table_exists("layer_serial_counter", S):
        return
    op.create_table(
        "layer_serial_counter",
        sa.Column(
            "layer_id",
            UUID_PG(as_uuid=True),
            sa.ForeignKey(f"{S}.layer.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("field_name", sa.Text(), primary_key=True, nullable=False),
        sa.Column("last_value", sa.BigInteger(), nullable=False),
        sa.Column(
            "updated_at",
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        schema=S,
    )


def downgrade() -> None:
    # Without the table geoapi falls back to max + 1, so a downgrade loses
    # only the protection against reusing a deleted highest number.
    h.drop_table_if_present("layer_serial_counter", S)
