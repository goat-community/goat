from typing import List
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field, ValidationError, validator
from src.schemas.content import ContentUpdateBase
from src.db.models.layer import (
    FeatureLayerBase,
    LayerBase,
    GeospatialAttributes,
    layer_base_example,
    feature_layer_base_example,
    geospatial_attributes_example,
)

from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape


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
# Layer Base for Read
################################################################################


class ReadBase(BaseModel):
    extent: dict
    content_id: UUID = Field(..., description="Content ID of the layer", alias="id")

    @validator("extent", pre=True)
    def wkt_to_geojson(cls, v):
        if v and isinstance(v, WKBElement):
            return to_shape(v).__geo_interface__
        else:
            return v

    # @validator("id", pre=True)
    # def populate_id(cls, v, values):
    #     return values.get("content_id")
    class Config:
        allow_population_by_field_name = True


################################################################################
# Layer Base DTOs
################################################################################


class LayerUpdateBase(ContentUpdateBase):
    """Base model for layer updates."""

    group: str | None = Field(None, description="Layer group name")
    data_reference_year: int | None = Field(None, description="Data reference year")


################################################################################
# Feature Layer DTOs
################################################################################


class FeatureLayerReadBase(FeatureLayerBase, ReadBase):
    pass


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
    data_source: str = Field(
        ...,
        description="Data source name",
    )
    data_reference_year: int | None


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
    payload: dict = Field(..., description="Used Request payload to compute the indicator")
    opportunities: List[UUID] | None = Field(
        None, description="Opportunity data sets that are used to intersect with the indicator"
    )


feature_layer_indicator_attributes_example = {
    "indicator_type": "isochrone",
    "payload": {},
    "opportunities": [],
}


class FeatureLayerIndicatorCreate(FeatureLayerBase, FeatureLayerIndicatorAttributesBase):
    """Model to create feature layer indicator."""

    pass


class FeatureLayerIndicatorRead(FeatureLayerReadBase, FeatureLayerIndicatorAttributesBase):
    """Model to read a feature layer indicator."""

    pass


class FeatureLayerIndicatorUpdate(FeatureLayerUpdateBase):
    """Model to update a feature layer indicator."""

    payload: dict | None = Field(None, description="Used Request payload to compute the indicator")
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


feature_layer_scenario_attributes_example = {
    "scenario_id": 1,
    "scenario_type": "point",
    "feature_layer_type": "scenario",
}


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


imagery_layer_attributes_example = {
    "url": "https://geodata.nationaalgeoregister.nl/luchtfoto/rgb/wms?request=GetCapabilities&service=WMS",
    "data_type": "wms",
    "legend_urls": [
        "https://geodata.nationaalgeoregister.nl/luchtfoto/rgb/wms?request=GetLegendGraphic&service=WMS&layer=Actueel_ortho25&format=image/png&width=20&height=20",
        "https://geodata.nationaalgeoregister.nl/luchtfoto/rgb/wms?request=GetLegendGraphic&service=WMS&layer=Actueel_ortho25&format=image/png&width=20&height=20",
    ],
    "type": "imagery_layer",
}


class ImageryLayerCreate(LayerBase, GeospatialAttributes, ImageryLayerAttributesBase):
    """Model to create a imagery layer."""

    pass


class ImageryLayerRead(LayerBase, GeospatialAttributes, ImageryLayerAttributesBase, ReadBase):
    """Model to read a imagery layer."""

    pass


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


tile_layer_attributes_example = {
    "url": "https://geodata.nationaalgeoregister.nl/luchtfoto/rgb/wmts?request=GetCapabilities&service=WMTS",
    "data_type": "mvt",
    "type": "tile_layer",
}


class TileLayerCreate(LayerBase, GeospatialAttributes, TileLayerAttributesBase):
    """Model to create a tile layer."""

    pass


class TileLayerRead(LayerBase, GeospatialAttributes, TileLayerAttributesBase, ReadBase):
    """Model to read a tile layer."""

    pass


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


class TableLayerRead(LayerBase, ReadBase):
    pass


class TableLayerUpdate(LayerUpdateBase):
    pass


class TableLayerProject(LayerBase, LayerProjectAttributesBase):
    id: UUID = Field(..., description="Layer UUID")


def get_layer_class(class_type: str, **kwargs):
    layer_creator_class = {
        "table": TableLayerCreate,
        "tile_layer": TileLayerCreate,
        "imagery_layer": ImageryLayerCreate,
        "feature_layer": {
            "standard": FeatureLayerStandardCreate,
            "indicator": FeatureLayerIndicatorCreate,
            "scenario": FeatureLayerScenarioCreate,
        },
    }
    try:
        layer_type = kwargs["type"]
    except KeyError:
        raise ValidationError("Layer type is required")

    layer_class = layer_creator_class[layer_type]
    if layer_type == "feature_layer":
        try:
            feature_layer_type = kwargs["feature_layer_type"]
        except KeyError:
            raise ValidationError("Feature layer type is required")

        layer_class = layer_class[feature_layer_type]

    layer_class_name = layer_class.__name__
    if class_type == "read":
        layer_class_name = layer_class_name.replace("Create", "Read")
    elif class_type == "update":
        layer_class_name = layer_class_name.replace("Create", "Update")
    elif class_type == "create":
        pass
    else:
        raise ValueError(f"Layer class type ({class_type}) is invalid")

    return globals()[layer_class_name]


class LayerCreate(BaseModel):
    def __new__(cls, *args, **kwargs):
        layer_create_class = get_layer_class("create", **kwargs)
        return layer_create_class(**kwargs)


class LayerRead(BaseModel):
    def __new__(cls, *args, **kwargs):
        layer_read_class = get_layer_class("read", **kwargs)
        return layer_read_class(**kwargs)


def build_layer_object(data: dict):
    layer_class = {
        "table": TableLayerCreate,
        "tile_layer": TileLayerCreate,
        "imagery_layer": ImageryLayerCreate,
        "feature_layer": {
            "standard": FeatureLayerStandardCreate,
            "indicator": FeatureLayerIndicatorCreate,
            "scenario": FeatureLayerScenarioCreate,
        },
    }
    layer_type = data["type"]
    if layer_type == "feature_layer":
        layer_class = layer_class[layer_type][data["feature_layer_type"]]
    else:
        layer_class = layer_class[layer_type]

    return layer_class(**data)


def read_layer(layer_in, creator_layer):
    creator_class_name = creator_layer.__class__.__name__
    read_class_name = creator_class_name.replace("Create", "Read")
    read_class = globals()[read_class_name]
    return read_class.from_orm(layer_in)


request_examples = {
    "create": {
        "table_layer": {
            "summary": "Table Layer",
            "value": {
                **layer_base_example,
                "type": "table",
            },
        },
        "layer_standard": {
            "summary": "Layer Standard",
            "value": {
                **feature_layer_base_example,
                **geospatial_attributes_example,
                **layer_base_example,
            },
        },
        "layer_indicator": {
            "summary": "Layer Indicator",
            "value": {
                **feature_layer_base_example,
                **geospatial_attributes_example,
                **layer_base_example,
                **feature_layer_indicator_attributes_example,
                "feature_layer_type": "indicator",
            },
        },
        "layer_scenario": {
            "summary": "Layer Scenario",
            "value": {
                **feature_layer_base_example,
                **geospatial_attributes_example,
                **layer_base_example,
                **feature_layer_scenario_attributes_example,
            },
        },
        "imagery_layer": {
            "summary": "Imagery Layer",
            "value": {
                **layer_base_example,
                **geospatial_attributes_example,
                **imagery_layer_attributes_example,
            },
        },
        "tile_layer": {
            "summary": "Tile Layer",
            "value": {
                **layer_base_example,
                **geospatial_attributes_example,
                **tile_layer_attributes_example,
            },
        },
    },
}
