import uuid
from typing import List, Optional, Union
from pydantic import BaseModel, Field, validator
from uuid import UUID
from enum import Enum
from datetime import datetime


class ContentType(str, Enum):
    """Content types."""

    project = "project"
    layer = "layer"
    report = "report"
    style = "style"


class ProjectContentType(str, Enum):
    """Content types that can be stored in a project."""

    layer = "layer"
    report = "report"
    style = "style"


class ReportDataType(str, Enum):
    """Report export types."""

    pdf = "pdf"
    png = "png"
    # docx = "docx"
    # pptx = "pptx"
    # md = "md"
    html = "html"


class InitialViewState(BaseModel):
    """Model to show the initial view state of a project."""

    latitude: float = Field(..., description="Latitude", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude", ge=-180, le=180)
    zoom: int = Field(..., description="Zoom level", ge=0, le=20)
    min_zoom: int = Field(..., description="Minimum zoom level", ge=0, le=20)
    max_zoom: int = Field(..., description="Maximum zoom level", ge=0, le=20)
    bearing: int = Field(..., description="Bearing", ge=0, le=360)
    pitch: int = Field(..., description="Pitch", ge=0, le=60)

    @validator("max_zoom")
    def check_max_zoom(cls, max_zoom, values):
        min_zoom = values.get("min_zoom")
        if min_zoom is not None and max_zoom < min_zoom:
            raise ValueError("max_zoom should be greater than or equal to min_zoom")
        return max_zoom

    @validator("min_zoom")
    def check_min_zoom(cls, min_zoom, values):
        max_zoom = values.get("max_zoom")
        if max_zoom is not None and min_zoom > max_zoom:
            raise ValueError("min_zoom should be less than or equal to max_zoom")
        return min_zoom


class ContentBase(BaseModel):
    data_store_id: Optional[int] = Field(
        None, description="ID of the datastore where the data is saved."
    )
    name: str = Field(..., description="Content name")
    description: Optional[str] = Field(
        None, description="Content description"
    )
    tags: Optional[List[str]] = Field(None, description="Content tags")
    thumbnail_url: Optional[str] = Field(
        None, description="Content thumbnail URL"
    )
    content_type: ContentType = Field(
        ..., description="Content type"
    )
    created_at: datetime = Field(
        ..., description="Content creation date"
    )
    updated_at: datetime = Field(
        ..., description="Content last update date"
    )
    owner_id: UUID = Field(..., description="Content owner ID")


class Content(ContentBase):
    id: UUID = Field(..., description="Content ID")


class ContentCreate(ContentBase):
    pass


class StyleBase(Content):
    """Base model for styles."""

    style: dict = Field(..., description="Style object in the geostyler format")


class Style(StyleBase):
    id: UUID = Field(..., description="Content ID")


class StyleCreate(StyleBase):
    pass


class OpportunityType(str, Enum):
    """Opportunity types."""

    aoi = "aoi"
    poi = "poi"
    population = "population"


class Opportunity(BaseModel):
    """Model to show the opportunity data sets."""

    id: UUID = Field(..., description="Layer ID of the opportunity data sets")
    name: str = Field(..., description="Opportunity name")
    opportunity_type: OpportunityType = Field(..., description="Opportunity type")
    query: Optional[str] = Field(None, description="Opportunity query to filter the data")


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
    opportunity = "opportunity"
    scenario = "scenario"
    analysis_unit = "analysis_unit"


class IndicatorType(str, Enum):
    """Indicator types."""

    single_isochrone = "isochrone"
    multi_isochrone = "multi_isochrone"
    heatmap = "heatmap"
    oev_gueteklasse = "oev_gueteklasse"
    public_transport_frequency = "public_transport_frequency"


class ScenarioType(str, Enum):
    """Scenario types."""

    building = "building"
    poi = "poi"
    aoi = "aoi"
    way = "way"


class FeatureLayerDataType(str, Enum):
    """Feature layer data types."""

    geojson = "geojson"
    shapefile = "shapefile"
    geopackage = "geopackage"
    geobuf = "geobuf"
    csv = "csv"
    xlsx = "xlsx"
    kml = "kml"
    mvt = "mvt"
    wfs = "wfs"
    binary = "binary"


class ImageryLayerDataType(str, Enum):
    """Imagery layer data types."""

    wms = "wms"


class TileLayerDataType(str, Enum):
    """Tile layer data types."""

    xyz = "xyz"
    wmts = "wmts"
    mvt = "mvt"


class TableDataType(str, Enum):
    """Table data types."""

    csv = "csv"
    xlsx = "xlsx"
    json = "json"


class GeospatialAttributes(BaseModel):
    """Some general geospatial attributes."""

    min_zoom: Optional[int] = Field(None, description="Minimum zoom level")
    max_zoom: Optional[int] = Field(None, description="Maximum zoom level")


class LayerBase(Content):
    """Base model for layers."""

    type: LayerType = Field(..., description="Layer type")
    group: str = Field(..., description="Layer group name")
    project_ids: List[UUID] = Field(
        ...,
        description="Projects IDs that contain this content. This is not mandatory for layers as they can be stored in a project or not.",
    )
    active: Optional[bool] = Field(
        None, description="Layer is active or not when inside a project other this should be None"
    )
    data_source: str = Field(..., description="Data source")
    data_reference_year: int = Field(..., description="Data reference year")


class FeatureLayerBase(LayerBase, GeospatialAttributes):
    """Base model for feature layers."""

    style_id: UUID = Field(..., description="Style ID of the layer")
    active_style_rule: List[bool] = Field(
        ...,
        description="Array with the active style rules for the respective style in the style_url. This attribute should only be populated when the layer is inside a project.",
    )
    feature_layer_type: FeatureLayerType = Field(..., description="Feature layer type")
    data_type: FeatureLayerDataType = Field(..., description="Content data type")
    query: Optional[str] = Field(None, description="Opportunity query to filter the data")


class FeatureLayerStandard(FeatureLayerBase):
    pass


class FeatureLayerAnalysisUnit(FeatureLayerBase):
    pass


class FeatureLayerIndicator(FeatureLayerBase):
    """Model to show the indicator layers."""

    indicator_type: IndicatorType = Field(..., description="Indicator type")
    scenario_id: Optional[int] = Field(
        None, description="Scenario ID if there is a scenario associated with this layer"
    )
    payload: dict = Field(..., description="Used Request payload to compute the indicator")
    opportunities: List[Opportunity] = Field(
        ..., description="Opportunity data sets that are used to intersect with the indicator"
    )


class FeatureLayerOpportunity(FeatureLayerBase):
    """Model to show the opportunity layers."""

    opportunities: List[Opportunity] = Field(..., description="Opportunity data sets")
    active_opportunities: List[Opportunity] = Field(
        ..., description="Active opportunity data sets"
    )
    scenario_id: Optional[int] = Field(
        None, description="Scenario ID if there is a scenario associated with this layer"
    )


class FeatureLayerScenario(FeatureLayerBase):
    """Model to show the scenario layers."""

    scenario_type: ScenarioType = Field(..., description="Scenario type")
    scenario_id: int = Field(..., description="Scenario ID")


class ImageryLayerBase(LayerBase, GeospatialAttributes):
    """Base model for imagery layers."""

    url: str = Field(..., description="Layer URL")
    data_type: ImageryLayerDataType = Field(..., description="Content data type")
    legend_urls: List[str] = Field(..., description="Layer legend URLs")


class ImageryLayer(ImageryLayerBase):
    pass


class TileLayerBase(LayerBase):
    """Base model for tile layers."""

    url: str = Field(..., description="Layer URL")
    data_type: TileLayerDataType = Field(..., description="Content data type")


class TileLayer(TileLayerBase):
    pass


class TableLayerBase(LayerBase):
    """Base model for table layers."""

    data_type: TableDataType = Field(..., description="Content data type")


class TableLayer(TableLayerBase):
    pass

class Report(Content):
    project_id: UUID = Field(
        ...,
        description="Project ID that contains the report. This is mandatory for reports as they are always contained in a project.",
    )
    export_type: ReportDataType = Field(..., description="Report export type")


class ReportProject(Content):
    pass

class ProjectBase(ContentBase):
    initial_view_state: InitialViewState = Field(
        ..., description="Initial view state of the project"
    )
    reports: List[ReportProject] = Field(
        ..., description="List of reports contained in the project"
    )
    layers: List[
        Union[
            FeatureLayerAnalysisUnit,
            FeatureLayerIndicator,
            FeatureLayerOpportunity,
            FeatureLayerStandard,
            TableLayer,
            TileLayer,
            ImageryLayer,
        ]
    ] = Field(..., description="List of layers contained in the project")

class Project(ProjectBase):
    uuid: UUID = Field(..., description="Project UUID")

class ProjectCreate(ProjectBase):
    pass
