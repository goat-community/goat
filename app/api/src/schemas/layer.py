from enum import Enum
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, ValidationError

from src.db.models._base_class import DateTimeBase, content_base_example
from src.db.models.layer import (
    FeatureLayerType,
    GeospatialAttributes,
    ImageryLayerDataType,
    IndicatorType,
    LayerBase,
    LayerType,
    ScenarioType,
    TileLayerDataType,
    geospatial_attributes_example,
    layer_base_example,
)


class AnalysisType(str, Enum):
    """Analysis types."""

    intersects = "intersects"


# TODO: Differentiate the types here into import and export types?


class TableDataType(str, Enum):
    """Table data types."""

    csv = "csv"
    xlsx = "xlsx"
    json = "json"


class LayerReadBaseAttributes(BaseModel):
    id: UUID = Field(..., description="Content ID of the layer", alias="id")
    user_id: UUID = Field(..., description="User ID of the owner")
    type: LayerType = Field(..., description="Layer type")


class LayerCreateBaseAttributes(BaseModel):
    type: LayerType = Field(..., description="Layer type")


################################################################################
# LayerBase
################################################################################


class FeatureLayerBase(LayerBase, GeospatialAttributes):
    """Base model for feature layers."""

    data_store_id: UUID = Field(..., description="Data store ID of the layer")
    feature_layer_type: "FeatureLayerType" = Field(..., description="Feature layer type")
    size: int = Field(..., description="Size of the layer in bytes")
    style: dict = Field(..., description="Style of the layer")


feature_layer_base_example = {
    "size": 1000,
    "style": {
        "version": 8,
        "name": "GeoStyler Demo",
        "layers": [
            {
                "type": "line",
                "paint": {"line-color": "#ff0000", "line-width": 5},
                "id": "r0_sy0_st0",
            }
        ],
        "metadata": {
            "geostyler:ref": {"rules": [{"name": "Rule 1", "symbolizers": [["r0_sy0_st0"]]}]}
        },
    },
}

################################################################################
# Feature Layer DTOs
################################################################################
# Base models


class FeatureLayerSpecificAttributes(BaseModel):
    feature_layer_type: "FeatureLayerType" = Field(..., description="Feature layer type")
    size: int = Field(..., description="Size of the layer in bytes")
    style: dict = Field(..., description="Style of the layer")
    query: str | None = Field(None, description="Query to filter the layer data")


class FeatureLayerCreateBase(
    LayerCreateBaseAttributes, LayerBase, FeatureLayerSpecificAttributes, GeospatialAttributes
):
    """Base model for feature layer creates."""

    pass


class FeatureLayerLayerReadBaseAttributes(
    LayerReadBaseAttributes, LayerBase, FeatureLayerSpecificAttributes, GeospatialAttributes
):
    """Base model for feature layer reads."""

    pass


class FeatureLayerUpdateBase(LayerBase, FeatureLayerSpecificAttributes, GeospatialAttributes):
    """Base model for feature layer updates."""

    style: dict | None = Field(None, description="Style ID of the layer")
    size: int | None = Field(None, description="Size of the layer in bytes")


feature_layer_update_base_example = {
    "style": [
        "match",
        ["get", "category"],
        ["forest"],
        "hsl(137, 37%, 30%)",
        ["park"],
        "hsl(135, 100%, 100%)",
        "#000000",
    ],
    "size": 1000,
}


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


# Feature Layer Standard
class IFeatureLayerStandardCreate(FeatureLayerCreateBase):
    pass


class IFeatureLayerStandardRead(FeatureLayerLayerReadBaseAttributes, DateTimeBase):
    pass


class IFeatureLayerStandardUpdate(FeatureLayerUpdateBase):
    pass


# Feature Layer Indicator
class FeatureLayerIndicatorAttributesBase(BaseModel):
    """Base model for additional attributes feature layer indicator."""

    indicator_type: IndicatorType = Field(..., description="Indicator type")


feature_layer_indicator_attributes_example = {
    "indicator_type": "isochrone",
}


class IFeatureLayerIndicatorCreate(FeatureLayerCreateBase, FeatureLayerIndicatorAttributesBase):
    """Model to create feature layer indicator."""

    pass


class IFeatureLayerIndicatorRead(
    FeatureLayerLayerReadBaseAttributes, FeatureLayerIndicatorAttributesBase, DateTimeBase
):
    """Model to read a feature layer indicator."""

    pass


class IFeatureLayerIndicatorUpdate(FeatureLayerUpdateBase):
    """Model to update a feature layer indicator."""

    pass


# Feature Layer Scenario
class FeatureLayerScenarioAttributesBase(BaseModel):
    """Base model for additional attributes feature layer scenario."""

    scenario_id: UUID = Field(..., description="Scenario ID of the scenario layer.")
    scenario_type: ScenarioType = Field(..., description="Scenario type")


feature_layer_scenario_attributes_example = {
    "scenario_id": "60a42459-11c8-4cd7-91f1-091d0e05a4a3",
    "scenario_type": "point",
}


class IFeatureLayerScenarioCreate(FeatureLayerCreateBase, FeatureLayerScenarioAttributesBase):
    """Model to create feature layer scenario."""

    pass


class IFeatureLayerScenarioRead(
    FeatureLayerLayerReadBaseAttributes, FeatureLayerScenarioAttributesBase, DateTimeBase
):
    """Model to read a feature layer scenario."""

    pass


class IFeatureLayerScenarioUpdate(FeatureLayerUpdateBase):
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
}


class IImageryLayerCreate(
    LayerCreateBaseAttributes, LayerBase, GeospatialAttributes, ImageryLayerAttributesBase
):
    """Model to create a imagery layer."""

    pass


class IImageryLayerRead(
    LayerReadBaseAttributes,
    LayerBase,
    GeospatialAttributes,
    ImageryLayerAttributesBase,
    DateTimeBase,
):
    """Model to read a imagery layer."""

    pass


class IImageryLayerUpdate(LayerBase, GeospatialAttributes):
    """Model to"""

    url: str | None = Field(None, description="Layer URL")
    legend_urls: List[str] | None = Field(None, description="Layer legend URLs")


imagery_layer_update_base_example = {
    "url": "https://geodata.nationaalgeoregister.nl/luchtfoto/rgb/wms?request=GetCapabilities&service=WMS",
    "legend_urls": [
        "https://geodata.nationaalgeoregister.nl/luchtfoto/rgb/wms?request=GetLegendGraphic&service=WMS&layer=Actueel_ortho25&format=image/png&width=20&height=20",
        "https://geodata.nationaalgeoregister.nl/luchtfoto/rgb/wms?request=GetLegendGraphic&service=WMS&layer=Actueel_ortho25&format=image/png&width=20&height=20",
    ],
}

################################################################################
# Tile Layer DTOs
################################################################################


class TileLayerAttributesBase(BaseModel):
    """Base model for additional attributes tile layer."""

    url: str = Field(..., description="Layer URL")
    data_type: TileLayerDataType = Field(..., description="Content data type")


tile_layer_attributes_example = {
    "url": "https://goat.plan4better.de/api/v1/layers/tiles/accidents_pedestrians/12/2179/1420.pbf",
    "data_type": "mvt",
}


class ITileLayerCreate(
    LayerCreateBaseAttributes, LayerBase, GeospatialAttributes, TileLayerAttributesBase
):
    """Model to create a tile layer."""

    pass


class ITileLayerRead(
    LayerReadBaseAttributes, LayerBase, GeospatialAttributes, TileLayerAttributesBase, DateTimeBase
):
    """Model to read a tile layer."""

    pass


class ITileLayerUpdate(LayerBase, GeospatialAttributes):
    """Model to update a tile layer."""

    url: str | None = Field(None, description="Layer URL")


tile_layer_update_example = {
    "url": "https://geodata.nationaalgeoregister.nl/luchtfoto/rgb/wmts?request=GetCapabilities&service=WMTS"
}

################################################################################
# Table Layer DTOs
################################################################################


class ITableLayerCreate(LayerCreateBaseAttributes, LayerBase):
    pass


class ITableLayerRead(LayerBase, LayerReadBaseAttributes, DateTimeBase):
    pass


class ITableLayerUpdate(LayerBase):
    pass


def get_layer_class(class_type: str, **kwargs):
    layer_creator_class = {
        "table": ITableLayerCreate,
        "tile_layer": ITileLayerCreate,
        "imagery_layer": IImageryLayerCreate,
        "feature_layer": {
            "standard": IFeatureLayerStandardCreate,
            "indicator": IFeatureLayerIndicatorCreate,
            "scenario": IFeatureLayerScenarioCreate,
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


class ILayerCreate(BaseModel):
    def __new__(cls, *args, **kwargs):
        layer_create_class = get_layer_class("create", **kwargs)
        return layer_create_class(**kwargs)


class ILayerRead(BaseModel):
    def __new__(cls, *args, **kwargs):
        layer_read_class = get_layer_class("read", **kwargs)
        return layer_read_class(**kwargs)


class ILayerUpdate(BaseModel):
    def __new__(cls, *args, **kwargs):
        layer_update_class = get_layer_class("update", **kwargs)
        return layer_update_class(**kwargs)


request_examples = {
    "get": {
        "ids": ["e7dcaae4-1750-49b7-89a5-9510bf2761ad", "e7dcaae4-1750-49b7-89a5-9510bf2761ad"],
    },
    "create": {
        "table_layer": {
            "summary": "Table Layer",
            "value": {
                **content_base_example,
                **layer_base_example,
                "type": "table",
            },
        },
        "layer_standard": {
            "summary": "Layer Standard",
            "value": {
                **content_base_example,
                **feature_layer_base_example,
                **geospatial_attributes_example,
                **layer_base_example,
                "type": "feature_layer",
                "feature_layer_type": "standard",
            },
        },
        "layer_indicator": {
            "summary": "Layer Indicator",
            "value": {
                **content_base_example,
                **feature_layer_base_example,
                **geospatial_attributes_example,
                **layer_base_example,
                **feature_layer_indicator_attributes_example,
                "type": "feature_layer",
                "feature_layer_type": "indicator",
            },
        },
        "layer_scenario": {
            "summary": "Layer Scenario",
            "value": {
                **content_base_example,
                **feature_layer_base_example,
                **geospatial_attributes_example,
                **layer_base_example,
                **feature_layer_scenario_attributes_example,
                "type": "feature_layer",
                "feature_layer_type": "scenario",
            },
        },
        "imagery_layer": {
            "summary": "Imagery Layer",
            "value": {
                **content_base_example,
                **layer_base_example,
                **geospatial_attributes_example,
                **imagery_layer_attributes_example,
                "type": "imagery_layer",
            },
        },
        "tile_layer": {
            "summary": "Tile Layer",
            "value": {
                **content_base_example,
                **layer_base_example,
                **geospatial_attributes_example,
                **tile_layer_attributes_example,
                "type": "tile_layer",
            },
        },
    },
    "update": {
        "table_layer": {
            "summary": "Table Layer",
            "value": {
                **content_base_example,
                **layer_base_example,
            },
        },
    },
}
