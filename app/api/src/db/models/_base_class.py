from sqlmodel import Field, SQLModel, Column, DateTime, text
from datetime import datetime
from typing import Optional

class DateTimeBase(SQLModel):
    """Base class for models with created_at and updated_at fields."""

    updated_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=False, onupdate=datetime.utcnow),
        default_factory=datetime.utcnow,
    )
    created_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    )
