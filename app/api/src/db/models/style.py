from pydantic import Field
from uuid import UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, text, ForeignKey, Text, Relationship, SQLModel
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .content import Content
    from .layer import Layer


class StyleBase(SQLModel):
    """Base model for styles."""

    style: dict = Field(
        sa_column=Column(JSONB), description="Style object in the geostyler format"
    )


class Style(StyleBase):
    __tablename__ = "style"
    __table_args__ = {"schema": "customer"}

    content_id: UUID = Field(
        sa_column=Column(
            Text,
            ForeignKey("customer.content.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        description="Content ID",
    )

    # Relationships
    content: "Content" = Relationship(
        back_populates="style"
    )
    layers: List["Layer"] = Relationship(
        back_populates="style"
    )