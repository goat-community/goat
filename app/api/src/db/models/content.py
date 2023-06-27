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
from ._base_class import UUIDAutoBase, DateTimeBase
from sqlalchemy.orm import mapper, relationship
if TYPE_CHECKING:
    from .style import Style
    from .report import Report
    from .layer import Layer
    from .project import Project
    from .user import User
    from src.schemas.content import ContentType


# TODO: Trigger to update the date when the content is updated
class ContentBase(SQLModel):
    name: str = Field(sa_column=Column(Text, nullable=False), description="Content name")
    description: Optional[str] = Field(sa_column=Column(Text), description="Content description")
    tags: Optional[List[str]] = Field(sa_column=ARRAY(Text()), description="Content tags")
    thumbnail_url: Optional[str] = Field(
        sa_column=Column(Text), description="Content thumbnail URL"
    )
    content_type: "ContentType" = Field(
        sa_column=Column(Text, nullable=False), description="Content type"
    )
    user_id: UUID = Field(
        sa_column=Column(
            Text,
            ForeignKey("customer.user.id", ondelete="CASCADE"),
            nullable=False,
        ),
        description="Content owner ID",
    )


class Content(UUIDAutoBase, DateTimeBase, ContentBase, table=True):
    __tablename__ = "content"
    __table_args__ = {"schema": "customer"}

    user_id: UUID = Field(
        sa_column=Column(
            Text,
            ForeignKey("customer.user.id", ondelete="CASCADE"),
            nullable=False,
        ),
        description="Content owner ID",
    )

    # Relationships
    user: "User" = Relationship(back_populates="contents")
    style: "Style" = Relationship(
        back_populates="content", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    project: "Project" = Relationship(
        back_populates="content", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    layer: "Layer" = Relationship(
        back_populates="content", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    report: "Report" = Relationship(
        back_populates="content", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )