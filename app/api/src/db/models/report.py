from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import text
from sqlmodel import Column, Field, ForeignKey, Relationship
from sqlalchemy.dialects.postgresql import UUID as UUID_PG
from src.db.models._base_class import DateTimeBase, ContentBaseAttributes

if TYPE_CHECKING:
    from .project import Project


class Report(DateTimeBase, ContentBaseAttributes, table=True):
    __tablename__ = "report"
    __table_args__ = {"schema": "customer"}

    id: UUID | None = Field(
        sa_column=Column(
            UUID_PG(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=text("uuid_generate_v4()"),
        ),
        description="Layer ID",
    )
    user_id: UUID = Field(
        sa_column=Column(
            UUID_PG(as_uuid=True),
            ForeignKey("customer.user.id", ondelete="CASCADE"),
            nullable=False,
        ),
        description="Project owner ID",
    )
    folder_id: UUID = Field(
        sa_column=Column(
            UUID_PG(as_uuid=True),
            ForeignKey("customer.folder.id", ondelete="CASCADE"),
            nullable=False,
        ),
        description="Project folder ID",
    )
    project_id: UUID = Field(
        sa_column=Column(
            UUID_PG(as_uuid=True),
            ForeignKey("customer.project.id", ondelete="CASCADE"),
            nullable=False,
        ),
        description="Project ID that contains the report. This is mandatory for reports as they are always contained in a project.",
    )
    report: dict = Field(sa_column=Column(JSONB), description="Report object in JSON Format")

    # Relationships
    project: "Project" = Relationship(back_populates="reports")

Report.update_forward_refs()