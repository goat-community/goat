from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import (
    ForeignKey,
    Column,
    DateTime,
    Field,
    SQLModel,
    Text,
    text,
    ARRAY,
    Relationship,
)
from uuid import UUID
from enum import Enum
from pydantic import BaseModel
from sqlalchemy import event
from sqlalchemy.orm import mapper, relationship
from src.db.models.content import ContentBase, Content

# from .project import Project

if TYPE_CHECKING:
    from .style import Style
    from .report import Report
    from .layer import Layer

    from .project import Project
    from .user import User


class ContentType(str, Enum):
    """Content types."""

    project = "project"
    layer = "layer"
    report = "report"
    style = "style"


class ContentCreate(ContentBase):
    pass


class ContentUpdateBase(BaseModel):
    name: Optional[str] = Field(None, description="Content name")
    description: Optional[str] = Field(None, description="Content description")
    tags: Optional[List[str]] = Field(None, description="Content tags")
    thumbnail_url: Optional[str] = Field(None, description="Content thumbnail URL")
    owner_id: Optional[UUID] = Field(None, description="Content owner ID")


class ContentUpdate(ContentUpdateBase):
    pass


class ContentRead(Content):
    pass


class UUIDFKContent(SQLModel):
    id: UUID = Field(
        sa_column=Column(
            Text,
            ForeignKey("customer.content.id", ondelete="CASCADE"),
            nullable=False,
            primary_key=True,
        ),
        description="Content UUID",
    )
