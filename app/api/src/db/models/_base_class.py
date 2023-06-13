from sqlmodel import Field, SQLModel, Text, Column, DateTime, text
from uuid import uuid4, UUID
from datetime import datetime
from typing import Optional

class UUIDBase(SQLModel):
    """Base class for models with UUID primary key."""

    id: UUID = Field(sa_column=Column(Text, primary_key=True, nullable=False))


class UUIDAutoBase(SQLModel):
    """Base class for models with UUID primary key. The UUID is generated automatically."""

    id: Optional[UUID] = Field(
        sa_column=Column(Text, primary_key=True, nullable=False, server_default=text("uuid_generate_v4()"))
    )


class DateTimeBase(SQLModel):
    """Base class for models with created_at and updated_at fields."""

    updated_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=False, onupdate=datetime.utcnow),
        default_factory=datetime.utcnow,
    )
    created_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP()"))
    )
