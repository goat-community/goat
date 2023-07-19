from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, Field, ForeignKey, Relationship, SQLModel, Text

if TYPE_CHECKING:
    from .content import Content
    from .project import Project


class ReportBase(SQLModel):
    """Base model for styles."""

    project_id: UUID = Field(
        sa_column=Column(
            Text, ForeignKey("customer.project.id", ondelete="CASCADE"), nullable=False
        ),
        description="Project ID that contains the report. This is mandatory for reports as they are always contained in a project.",
    )
    report: dict = Field(sa_column=Column(JSONB), description="Report object in JSON Format")


class Report(ReportBase, table=True):
    __tablename__ = "report"
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
    project_id: UUID = Field(
        sa_column=Column(
            Text, ForeignKey("customer.project.content_id", ondelete="CASCADE"), nullable=False
        ),
        description="Project ID that contains the report. This is mandatory for reports as they are always contained in a project.",
    )

    # Relationships
    content: "Content" = Relationship(
        back_populates="report",
    )
    project: "Project" = Relationship(back_populates="reports")
