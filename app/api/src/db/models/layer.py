from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union
from sqlmodel import (
    ForeignKey,
    Column,
    DateTime,
    Field,
    SQLModel,
    Text,
    text,
    ARRAY,
    Integer,
    Boolean,
    Relationship,
)
from uuid import UUID
from enum import Enum
from sqlalchemy.dialects.postgresql import JSONB
from pydantic import BaseModel
from sqlalchemy import event
from sqlalchemy.orm import mapper, relationship

if TYPE_CHECKING:
    from .content import Content
    from .style import Style
    from .scenario import Scenario
    from .project import Project
    from schemas.layer import (
        FeatureLayerType,
        ImageryLayerDataType,
        TileLayerDataType,
        IndicatorType,
        ScenarioType,
        LayerType,
    )


class GeospatialAttributes(SQLModel):
    """Some general geospatial attributes."""

    min_zoom: Optional[int] = Field(
        sa_column=Column(Integer, nullable=True), description="Minimum zoom level"
    )
    max_zoom: Optional[int] = Field(
        sa_column=Column(Integer, nullable=True), description="Maximum zoom level"
    )


class LayerBase(SQLModel):
    """Base model for layers."""

    type: "LayerType" = Field(sa_column=Column(Text, nullable=False), description="Layer type")
    group: str = Field(sa_column=Column(Text, nullable=True), description="Layer group name")
    data_source_id: int = Field(
        sa_column=Column(Integer, ForeignKey("customer.data_source.id")), description="Data source"
    )
    data_reference_year: int = Field(sa_column=Column(Integer), description="Data reference year")


# Base models
class FeatureLayerBase(LayerBase, GeospatialAttributes):
    """Base model for feature layers."""

    style_id: UUID = Field(
        sa_column=Column(Text, ForeignKey("customer.style.id")),
        description="Style ID of the layer",
    )
    feature_layer_type: "FeatureLayerType" = Field(
        sa_column=Column(Text, nullable=False), description="Feature layer type"
    )
    size: int = Field(
        sa_column=Column(Integer, nullable=False), description="Size of the layer in bytes"
    )


# TODO: Relation to check if opportunities_uuids exist in layers
class Layer(FeatureLayerBase, table=True):
    __tablename__ = "layer"
    __table_args__ = {"schema": "customer"}

    content_id: UUID = Field(
        sa_column=Column(
            Text, ForeignKey("customer.content.id", ondelete="CASCADE"), primary_key=True
        ),
        description="Layer UUID",
    )
    url: Optional[str] = Field(
        sa_column=Column(Text, nullable=True), description="Layer URL for tile and imagery layers"
    )
    data_type: Optional[Union["ImageryLayerDataType", "TileLayerDataType"]] = Field(
        sa_column=Column(Text, nullable=True),
        description="Data type for imagery layers and tile layers",
    )
    legend_urls: Optional[List[str]] = Field(
        sa_column=Column(ARRAY(Text()), nullable=True),
        description="Layer legend URLs for imagery layers.",
    )
    indicator_type: Optional["IndicatorType"] = Field(
        sa_column=Column(Text, nullable=True),
        description="If it is an indicator layer, the indicator type",
    )
    scenario_id: Optional[int] = Field(
        sa_column=Column(Integer, ForeignKey("customer.scenario.id"), nullable=True),
        description="Scenario ID if there is a scenario associated with this layer",
    )
    scenario_type: Optional["ScenarioType"] = Field(
        sa_column=Column(Text, nullable=True),
        description="Scenario type if the layer is a scenario layer",
    )
    payload: Optional[dict] = Field(
        sa_column=Column(JSONB, nullable=True),
        description="Used Request payload to compute the indicator",
    )
    opportunities: Optional[List[UUID]] = Field(
        sa_column=Column(ARRAY(Text()), nullable=True),
        description="Opportunity data sets that are used to intersect with the indicator",
    )

    # Relationships

    content: "Content" = Relationship(back_populates="layer")
    scenario: "Scenario" = Relationship(back_populates="layers")
    style: "Style" = Relationship(back_populates="layers")
    
