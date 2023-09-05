from sqlmodel import Field, SQLModel, Column, DateTime, text
from datetime import datetime
from typing import Optional, Any, List
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.dialects.postgresql import UUID as UUID_PG
from sqlalchemy import ForeignKey, Text, ARRAY
from uuid import UUID

class DateTimeBase(SQLModel):
    """Base class for models with created_at and updated_at fields."""

    updated_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=False, onupdate=datetime.utcnow),
        default_factory=datetime.utcnow,
    )
    created_at: Optional[datetime] = Field(
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    )

class ContentBaseAttributes(SQLModel):
    """Base model for content attributes."""

    folder_id: UUID = Field(
        sa_column=Column(
            UUID_PG(as_uuid=True),
            ForeignKey("customer.folder.id", ondelete="CASCADE"),
            nullable=False,
        ),
        description="Layer folder ID",
    )
    name: str = Field(sa_column=Column(Text, nullable=False), description="Layer name", max_length=255)
    description: str | None = Field(sa_column=Column(Text), description="Layer description", max_length=2000)
    tags: List[str] | None = Field(
        sa_column=Column(ARRAY(Text()), nullable=True), description="Layer tags"
    )
    thumbnail_url: str | None = Field(
        sa_column=Column(Text, nullable=True), description="Layer thumbnail URL"
    )

content_base_example = {
    "folder_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "Layer name",
    "description": "Layer description",
    "tags": ["tag1", "tag2"],
    "thumbnail_url": "https://goat-app-assets.s3.eu-central-1.amazonaws.com/logos/goat_green.png",
}


@as_declarative()
class Base:
    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
