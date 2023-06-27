from typing import TYPE_CHECKING, List
from sqlmodel import (
    ForeignKey,
    Column,
    Field,
    SQLModel,
    Text,
    text,
    Relationship,
)
from uuid import UUID
from sqlalchemy.dialects.postgresql import JSONB
from ._base_class import UUIDAutoBase

if TYPE_CHECKING:
    from .report import Report
    from .content import Content
    from schemas.project import InitialViewState


class Project(UUIDAutoBase, table=True):
    __tablename__ = "project"
    __table_args__ = {"schema": "customer"}

    content_id: UUID = Field(
        sa_column=Column(
            Text,
            ForeignKey("customer.content.id", ondelete="CASCADE"),
            nullable=False,
            primary_key=True,
        ),
        description="Content UUID",
    )
    initial_view_state: "InitialViewState" = Field(
        sa_column=Column(JSONB, nullable=False), description="Initial view state of the project"
    )

    # Relationships
    content: "Content" = Relationship(back_populates="project")
    reports: List["Report"] = Relationship(
        back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    # layers: List[
    #     Union[
    #         "FeatureLayerAnalysisUnitProject",
    #         "FeatureLayerIndicatorProject",
    #         "FeatureLayerOpportunityProject",
    #         "FeatureLayerStandardProject",
    #         "TableLayerProject",
    #         "TileLayerProject",
    #         "ImageryLayerProject",
    #     ]
    # ] = Relationship(
    #     back_populates="project",
    #     sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    # )
