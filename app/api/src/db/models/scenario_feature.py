from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import (
    Column,
    Field,
    ForeignKey,
    Integer,
    Relationship,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as UUID_PG
from src.schemas.layer import ScenarioType

from ._base_class import DateTimeBase

if TYPE_CHECKING:
    from .layer import Layer


class ScenarioFeature(DateTimeBase, table=True):
    """Layer model."""

    __tablename__ = "scenario_feature"
    __table_args__ = {"schema": "customer"}

    id: UUID | None = Field(
        sa_column=Column(
            UUID_PG(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=text("uuid_generate_v4()"),
        )
    )
    feature_id: int = Field(
        sa_column=Column(Integer, nullable=False), description="Feature ID of the modified feature"
    )
    original_layer_id: str = Field(
        sa_column=Column(UUID_PG(as_uuid=True), ForeignKey("customer.layer.id")),
        description="Layer ID of the modified layer",
    )
    scenario_type: ScenarioType = Field(
        sa_column=Column(Text, nullable=False), description="Type of the scenario"
    )
    modification: dict = Field(
        sa_column=Column(JSONB), description="Modification object in JSON format"
    )

    # Relationships
    original_layer: "Layer" = Relationship(back_populates="scenario_features")
