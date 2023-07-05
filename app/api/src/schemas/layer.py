from typing import List
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field
from src.schemas.content import ContentUpdateBase
from src.db.models.layer import FeatureLayerBase, LayerBase, GeospatialAttributes


class LayerType(str, Enum):
    """Layer types that are supported."""

    feature_layer = "feature_layer"
    imagery_layer = "imagery_layer"
    tile_layer = "tile_layer"
    table = "table"


class FeatureLayerType(str, Enum):
    """Feature layer types."""

    standard = "standard"
    indicator = "indicator"
    scenario = "scenario"
    street_network = "street_network"


class IndicatorType(str, Enum):
    """Indicator types."""

    single_isochrone = "isochrone"
    multi_isochrone = "multi_isochrone"
    heatmap = "heatmap"
    oev_gueteklasse = "oev_gueteklasse"
    public_transport_frequency = "public_transport_frequency"


class AnalysisType(str, Enum):
    """Analysis types."""

    intersects = "intersects"


class ScenarioType(str, Enum):
    """Scenario types."""

    point = "point"
    polygon = "polygon"
    network_street = "network_street"

# TODO: Differentiate the types here into import and export types?


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

# Rename to Vector tiles?


class TileLayerDataType(str, Enum):
    """Tile layer data types."""

    mvt = "mvt"


class TableDataType(str, Enum):
    """Table data types."""

    csv = "csv"
    xlsx = "xlsx"
    json = "json"

################################################################################
# Layer Base DTOs
################################################################################


class LayerUpdateBase(ContentUpdateBase):
    """Base model for layer updates."""

    group: str | None = Field(None, description="Layer group name")
    data_source_id: int | None = Field(None, description="Data source")
    data_reference_year: int | None = Field(None, description="Data reference year")


################################################################################
# Feature Layer DTOs
################################################################################

class FeatureLayerReadBase(FeatureLayerBase):
    id: UUID = Field(..., description="Layer UUID")


class FeatureLayerUpdateBase(LayerUpdateBase, GeospatialAttributes):
    """Base model for feature layer updates."""

    style_id: UUID | None = Field(None, description="Style ID of the layer")
    size: int | None = Field(None, description="Size of the layer in bytes")


class LayerProjectAttributesBase(BaseModel):
    """Base model for the additional attributes of layers in a project."""

    active: bool = Field(
        ...,
        description="Layer is active or not in the project",
    )
    data_source_name: str = Field(
        ...,
        description="Data source name",
    )


class FeatureLayerProjectBase(FeatureLayerBase, LayerProjectAttributesBase):
    """Model for feature layer that are in projects."""

    id: UUID = Field(..., description="Layer UUID")
    group: str | None = Field(..., description="Layer group name")
    style_id: UUID = Field(
        ...,
        description="Style ID of the layer",
    )
    query: str | None = Field(None, description="Query to filter the layer data")


# Feature Layer Standard
class FeatureLayerStandardCreate(FeatureLayerBase):
    pass


class FeatureLayerStandardRead(FeatureLayerReadBase):
    pass


class FeatureLayerStandardUpdate(FeatureLayerUpdateBase):
    pass


class FeatureLayerStandardProject(FeatureLayerProjectBase):
    pass


# Feature Layer Indicator
class FeatureLayerIndicatorAttributesBase(BaseModel):
    """Base model for additional attributes feature layer indicator."""

    indicator_type: IndicatorType = Field(..., description="Indicator type")
    payload: dict = Field(...,
                          description="Used Request payload to compute the indicator")
    opportunities: List[UUID] | None = Field(
        None, description="Opportunity data sets that are used to intersect with the indicator"
    )


class FeatureLayerIndicatorCreate(FeatureLayerBase, FeatureLayerIndicatorAttributesBase):
    """Model to create feature layer indicator."""

    pass


class FeatureLayerIndicatorRead(FeatureLayerReadBase, FeatureLayerIndicatorAttributesBase):
    """Model to read a feature layer indicator."""

    pass


class FeatureLayerIndicatorUpdate(FeatureLayerUpdateBase):
    """Model to update a feature layer indicator."""

    payload: dict | None = Field(
        None, description="Used Request payload to compute the indicator"
    )
    opportunities: List[UUID] | None = Field(
        None, description="Opportunity data sets that are used to intersect with the indicator"
    )


class FeatureLayerIndicatorProject(FeatureLayerProjectBase, FeatureLayerIndicatorAttributesBase):
    """Model for feature layer indicator in a project."""

    pass


# Feature Layer Scenario
class FeatureLayerScenarioAttributesBase(BaseModel):
    """Base model for additional attributes feature layer scenario."""

    scenario_id: int = Field(..., description="Scenario ID of the scenario layer.")
    scenario_type: ScenarioType = Field(..., description="Scenario type")


class FeatureLayerScenarioCreate(FeatureLayerBase, FeatureLayerScenarioAttributesBase):
    """Model to create feature layer scenario."""

    pass


class FeatureLayerScenarioRead(FeatureLayerReadBase, FeatureLayerScenarioAttributesBase):
    """Model to read a feature layer scenario."""

    pass


class FeatureLayerScenarioUpdate(FeatureLayerUpdateBase):
    """Model to update a feature layer scenario."""

    pass

################################################################################
# Imagery Layer DTOs
################################################################################


class ImageryLayerAttributesBase(BaseModel):
    """Base model for additional attributes imagery layer."""

    url: str = Field(..., description="Layer URL")
    data_type: ImageryLayerDataType = Field(..., description="Content data type")
    legend_urls: List[str] = Field(..., description="Layer legend URLs")


class ImageryLayerCreate(LayerBase, GeospatialAttributes, ImageryLayerAttributesBase):
    """Model to create a imagery layer."""

    pass


class ImageryLayerRead(LayerBase, GeospatialAttributes, ImageryLayerAttributesBase):
    """Model to read a imagery layer."""

    id: UUID = Field(..., description="Layer UUID")


class ImageryLayerUpdate(LayerUpdateBase):
    """Model to"""

    url: str | None = Field(None, description="Layer URL")
    legend_urls: List[str] | None = Field(None, description="Layer legend URLs")


class ImageryLayerProject(LayerBase, ImageryLayerAttributesBase, LayerProjectAttributesBase):
    """Model for imagery layer in a project."""

    id: UUID = Field(..., description="Layer UUID")


################################################################################
# Tile Layer DTOs
################################################################################


class TileLayerAttributesBase(BaseModel):
    """Base model for additional attributes tile layer."""

    url: str = Field(..., description="Layer URL")
    data_type: TileLayerDataType = Field(..., description="Content data type")


class TileLayerCreate(LayerBase, GeospatialAttributes, TileLayerAttributesBase):
    """Model to create a tile layer."""

    pass


class TileLayerRead(LayerBase, GeospatialAttributes, TileLayerAttributesBase):
    """Model to read a tile layer."""

    id: UUID = Field(..., description="Layer UUID")


class TileLayerUpdate(LayerUpdateBase):
    """Model to update a tile layer."""

    url: str | None = Field(None, description="Layer URL")


class TileLayerProject(LayerBase, TileLayerAttributesBase, LayerProjectAttributesBase):
    """Model for tile layer in a project."""

    id: UUID = Field(..., description="Layer UUID")


################################################################################
# Table Layer DTOs
################################################################################


class TableLayerCreate(LayerBase):
    pass


class TableLayerRead(LayerBase):
    id: UUID = Field(..., description="Layer UUID")


class TableLayerUpdate(LayerUpdateBase):
    pass


class TableLayerProject(LayerBase, LayerProjectAttributesBase):
    id: UUID = Field(..., description="Layer UUID")
