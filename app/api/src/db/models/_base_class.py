from uuid import UUID
from sqlmodel import Field, SQLModel, Column, DateTime, text
from datetime import datetime
from typing import Optional, Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from pydantic import BaseModel
from pydantic import root_validator


class DateTimeBase(SQLModel):
    """Base class for models with created_at and updated_at fields."""

    updated_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=False, onupdate=datetime.utcnow),
        default_factory=datetime.utcnow,
    )
    created_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    )


@as_declarative()
class Base:
    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class UuidToStr(BaseModel):
    @root_validator
    def convert_uuid_to_str(cls, values):
        for key, value in values.items():
            if isinstance(value, UUID):
                values[key] = str(value)
        return values
