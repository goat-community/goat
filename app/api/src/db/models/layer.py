from typing import TYPE_CHECKING, Any, List, Union, Optional
from sqlmodel import (
    ForeignKey,
    Column,
    Field,
    SQLModel,
    Text,
    text,
    ARRAY,
    Integer,
    Relationship,
)
from uuid import UUID
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry
from ._base_class import UuidToStr

if TYPE_CHECKING:
    from .content import Content
    from .style import Style
    from .scenario import Scenario
    from .scenario_feature import ScenarioFeature
    from .data_store import DataStore
    from src.schemas.layer import (
        FeatureLayerType,
        ImageryLayerDataType,
        TileLayerDataType,
        IndicatorType,
        ScenarioType,
        LayerType,
    )
    from .analysis_request import AnalysisRequest


class GeospatialAttributes(SQLModel):
    """Some general geospatial attributes."""

    min_zoom: int | None = Field(
        sa_column=Column(Integer, nullable=True), description="Minimum zoom level"
    )
    max_zoom: int | None = Field(
        sa_column=Column(Integer, nullable=True), description="Maximum zoom level"
    )


geospatial_attributes_example = {
    "min_zoom": 0,
    "max_zoom": 10,
}


class LayerBase(SQLModel):
    """Base model for layers."""

    type: "LayerType" = Field(sa_column=Column(Text, nullable=False), description="Layer type")
    data_store_id: UUID | None = Field(
        sa_column=Column(Text, ForeignKey("customer.data_store.id")),
        description="Data store ID of the layer",
    )
    data_source: str | None = Field(
        sa_column=Column(Text, nullable=True),
        description="Data source of the layer",
    )
    data_reference_year: int | None = Field(
        sa_column=Column(Integer, nullable=True),
        description="Data reference year of the layer",
    )
    extent: str | Any = Field(
        sa_column=Column(
            Geometry(geometry_type="MultiPolygon", srid="4326", spatial_index=True),
            nullable=False,
        ),
        description="Geographical Extent of the layer",
    )


layer_base_example = {
    "type": "feature_layer",
    "data_source": "data_source plan4better example",
    "data_reference_year": 2020,
    "extent": "MULTIPOLYGON(((0 0, 0 1, 1 1, 1 0, 0 0)), ((2 2, 2 3, 3 3, 3 2, 2 2)))",
}


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


feature_layer_base_example = {
    "style_id": "d0f4c0e0-0f0f-4f0f-8f0f-0f0f0f0f0f0f",
    "feature_layer_type": "standard",
    "size": 1000,
}


# TODO: Relation to check if opportunities_uuids exist in layers
class Layer(FeatureLayerBase, UuidToStr, table=True):
    """Layer model."""

    __tablename__ = "layer"
    __table_args__ = {"schema": "customer"}

    type: "LayerType" = Field(sa_column=Column(Text, nullable=False), description="Layer type")

    content_id: UUID | None = Field(
        sa_column=Column(
            Text,
            ForeignKey("customer.content.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        description="Layer UUID",
    )
    data_store_id: UUID | None = Field(
        sa_column=Column(Text, ForeignKey("customer.data_store.id")),
        description="Data store ID of the layer",
    )
    style_id: UUID | None = Field(
        sa_column=Column(Text, ForeignKey("customer.style.content_id")),
        description="Style ID of the layer",
    )
    url: str | None = Field(
        sa_column=Column(Text, nullable=True), description="Layer URL for tile and imagery layers"
    )
    data_type: Optional[Union["ImageryLayerDataType", "TileLayerDataType"]] = Field(
        sa_column=Column(Text, nullable=True),
        description="Data type for imagery layers and tile layers",
    )
    legend_urls: List[str] | None = Field(
        sa_column=Column(ARRAY(Text()), nullable=True),
        description="Layer legend URLs for imagery layers.",
    )
    indicator_type: Optional["IndicatorType"] = Field(
        sa_column=Column(Text, nullable=True),
        description="If it is an indicator layer, the indicator type",
    )
    scenario_id: str | None = Field(
        sa_column=Column(Text, ForeignKey("customer.scenario.id"), nullable=True),
        description="Scenario ID if there is a scenario associated with this layer",
    )
    scenario_type: Optional["ScenarioType"] = Field(
        sa_column=Column(Text, nullable=True),
        description="Scenario type if the layer is a scenario layer",
    )
    payload: dict | None = Field(
        sa_column=Column(JSONB, nullable=True),
        description="Used Request payload to compute the indicator",
    )
    opportunities: List[UUID] | None = Field(
        sa_column=Column(ARRAY(Text()), nullable=True),
        description="Opportunity data sets that are used to intersect with the indicator",
    )

    # Make FeatureLayer attributes nullable
    feature_layer_type: Optional["FeatureLayerType"] = Field(
        sa_column=Column(Text, nullable=True), description="Feature layer type"
    )
    size: int | None = Field(
        sa_column=Column(Integer, nullable=True), description="Size of the layer in bytes"
    )

    # Relationships

    content: "Content" = Relationship(back_populates="layer")
    scenario: "Scenario" = Relationship(back_populates="layers")
    style: "Style" = Relationship(back_populates="layers")
    scenario_features: List["ScenarioFeature"] = Relationship(back_populates="original_layer")
    data_store: "DataStore" = Relationship(back_populates="layers")
    analysis_requests: List["AnalysisRequest"] = Relationship(back_populates="layer")

    @classmethod
    def update_forward_refs(cls):
        from src.schemas.layer import (
            FeatureLayerType,
            ImageryLayerDataType,
            TileLayerDataType,
            IndicatorType,
            ScenarioType,
            LayerType,
        )

        super().update_forward_refs(
            LayerType=LayerType,
            FeatureLayerType=FeatureLayerType,
            ImageryLayerDataType=ImageryLayerDataType,
            TileLayerDataType=TileLayerDataType,
            IndicatorType=IndicatorType,
            ScenarioType=ScenarioType,
        )

    @property
    def id(self) -> str:
        return str(self.content_id)

    id: str | None


Layer.update_forward_refs()
