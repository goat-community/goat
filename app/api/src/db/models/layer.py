from enum import Enum
from typing import TYPE_CHECKING, List, Optional, Union
from uuid import UUID

from geoalchemy2 import Geometry
from sqlmodel import (
    ARRAY,
    Column,
    Field,
    ForeignKey,
    Integer,
    Relationship,
    SQLModel,
    Text,
)
from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape
from pydantic import validator
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID as UUID_PG, JSONB
from src.db.models._base_class import DateTimeBase, ContentBaseAttributes

if TYPE_CHECKING:
    from .analysis_request import AnalysisRequest
    from .data_store import DataStore
    from .scenario import Scenario
    from .scenario_feature import ScenarioFeature
    from .project import Project
    from ._link_model import LayerProjectLink


class FeatureLayerType(str, Enum):
    """Feature layer types."""

    standard = "standard"
    indicator = "indicator"
    scenario = "scenario"
    street_network = "street_network"


class FeatureLayerExportType(str, Enum):
    """Feature layer data types."""

    geojson = "geojson"
    shapefile = "shapefile"
    geopackage = "geopackage"
    geobuf = "geobuf"
    csv = "csv"
    xlsx = "xlsx"
    kml = "kml"


class FeatureLayerServeType(str, Enum):
    mvt = "mvt"
    wfs = "wfs"
    binary = "binary"


class ImageryLayerDataType(str, Enum):
    """Imagery layer data types."""

    wms = "wms"
    xyz = "xyz"
    wmts = "wmts"


class IndicatorType(str, Enum):
    """Indicator types."""

    single_isochrone = "isochrone"
    multi_isochrone = "multi_isochrone"
    heatmap = "heatmap"
    oev_gueteklasse = "oev_gueteklasse"
    public_transport_frequency = "public_transport_frequency"


class LayerType(str, Enum):
    """Layer types that are supported."""

    feature_layer = "feature_layer"
    imagery_layer = "imagery_layer"
    tile_layer = "tile_layer"
    table = "table"


class ScenarioType(str, Enum):
    """Scenario types."""

    point = "point"
    polygon = "polygon"
    network_street = "network_street"


class TileLayerDataType(str, Enum):
    """Tile layer data types."""

    mvt = "mvt"

class FeatureLayerGeometryType(str, Enum):
    """Feature layer geometry types."""

    point = "point"
    line = "line"
    polygon = "polygon"

class GeospatialAttributes(SQLModel):
    """Some general geospatial attributes."""

    min_zoom: int | None = Field(
        sa_column=Column(Integer, nullable=True), description="Minimum zoom level"
    )
    max_zoom: int | None = Field(
        sa_column=Column(Integer, nullable=True), description="Maximum zoom level"
    )
    extent: str | None = Field(
        sa_column=Column(
            Geometry(geometry_type="MultiPolygon", srid="4326", spatial_index=True),
            nullable=True,
        ),
        description="Geographical Extent of the layer",
    )

    @validator("extent", pre=True)
    def wkt_to_geojson(cls, v):
        if v and isinstance(v, WKBElement):
            return to_shape(v).wkt
        else:
            return v


geospatial_attributes_example = {
    "min_zoom": 0,
    "max_zoom": 10,
    "extent": "MULTIPOLYGON(((0 0, 0 1, 1 1, 1 0, 0 0)), ((2 2, 2 3, 3 3, 3 2, 2 2)))",
}


class LayerBase(ContentBaseAttributes):
    """Base model for layers."""

    data_source: str | None = Field(
        sa_column=Column(Text, nullable=True),
        description="Data source of the layer",
    )
    data_reference_year: int | None = Field(
        sa_column=Column(Integer, nullable=True),
        description="Data reference year of the layer",
    )


layer_base_example = {
    "data_source": "data_source plan4better example",
    "data_reference_year": 2020,
}


# TODO: Relation to check if opportunities_uuids exist in layers
class Layer(LayerBase, GeospatialAttributes, DateTimeBase, table=True):
    """Layer model."""

    __tablename__ = "layer"
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
        description="Layer owner ID",
    )
    folder_id: UUID = Field(
        sa_column=Column(
            UUID_PG(as_uuid=True),
            ForeignKey("customer.folder.id", ondelete="CASCADE"),
            nullable=False,
        ),
        description="Layer folder ID",
    )
    type: LayerType = Field(sa_column=Column(Text, nullable=False), description="Layer type")
    data_store_id: UUID | None = Field(
        sa_column=Column(UUID_PG(as_uuid=True), ForeignKey("customer.data_store.id")),
        description="Data store ID of the layer",
    )
    extent: str | None = Field(
        sa_column=Column(
            Geometry(geometry_type="MultiPolygon", srid="4326", spatial_index=True),
            nullable=True,
        ),
        description="Geographical Extent of the layer",
    )
    style: dict | None = Field(
        sa_column=Column(JSONB, nullable=True),
        description="Style of the layer",
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
    indicator_type: Optional[IndicatorType] = Field(
        sa_column=Column(Text, nullable=True),
        description="If it is an indicator layer, the indicator type",
    )
    scenario_id: UUID | None = Field(
        sa_column=Column(UUID_PG(as_uuid=True), ForeignKey("customer.scenario.id"), nullable=True),
        description="Scenario ID if there is a scenario associated with this layer",
    )
    scenario_type: Optional["ScenarioType"] = Field(
        sa_column=Column(Text, nullable=True),
        description="Scenario type if the layer is a scenario layer",
    )
    feature_layer_type: Optional["FeatureLayerType"] = Field(
        sa_column=Column(Text, nullable=True), description="Feature layer type"
    )
    feature_layer_geometry_type: FeatureLayerGeometryType | None = Field(
        sa_column=Column(Text, nullable=True), description="Geometry type for feature layers"
    )
    size: int | None = Field(
        sa_column=Column(Integer, nullable=True), description="Size of the layer in bytes"
    )
    attribute_mapping: dict | None = Field(
        sa_column=Column(JSONB, nullable=True),
        description="Attribute mapping for feature layers",
    )

    # Relationships

    scenario: "Scenario" = Relationship(back_populates="layers")
    scenario_features: List["ScenarioFeature"] = Relationship(back_populates="original_layer")
    data_store: "DataStore" = Relationship(back_populates="layers")
    analysis_requests: List["AnalysisRequest"] = Relationship(back_populates="layer")
    layer_projects: List["LayerProjectLink"] = Relationship(back_populates="layer")

    @validator("extent", pre=True)
    def wkt_to_geojson(cls, v):
        if v and isinstance(v, WKBElement):
            return to_shape(v).wkt
        else:
            return v


Layer.update_forward_refs()
