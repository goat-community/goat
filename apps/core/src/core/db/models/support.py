from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, ForeignKey, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as UUID_PG
from sqlmodel import Column, Field, SQLModel

from core.core.config import settings


class SupportTicketRead(SQLModel, table=True):
    """How far a user has read a support ticket.

    One row per (user, Odoo ticket): the newest visible message id the user
    has seen. Odoo keeps no per-reader state for customers, so the unread
    dots and the header badge are computed against these markers. The ticket
    lives in Odoo only — ticket_id is Odoo's helpdesk.ticket id, not a FK.
    """

    __tablename__ = "support_ticket_read"
    __table_args__ = {"schema": settings.SCHEMA}

    user_id: UUID = Field(
        sa_column=Column(
            UUID_PG(as_uuid=True),
            ForeignKey(f"{settings.SCHEMA}.user.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        )
    )
    ticket_id: int = Field(
        sa_column=Column(BigInteger, primary_key=True, nullable=False)
    )
    last_seen_message_id: int = Field(sa_column=Column(BigInteger, nullable=False))
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
        ),
    )
