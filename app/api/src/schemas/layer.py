
from enum import Enum
from pydantic import BaseModel, Field, ValidationError, validator
from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape
from uuid import UUID
from src.db.models.style import Style
from src.db.models.layer import IndicatorType
from src.schemas.content import ContentUpdate
from src.db.models.content import Content, content_base_example
from src.db.models.layer import LayerBase, FeatureLayerBase, ScenarioType, ImageryLayerDataType, TileLayerDataType, feature_layer_base_example, geospatial_attributes_example, layer_base_example, feature_layer_indicator_attributes_example, feature_layer_scenario_attributes_example, imagery_layer_attributes_example, tile_layer_attributes_example
from src.db.models.data_store import DataStore
from src.db.models.scenario import Scenario


class AnalysisType(str, Enum):
    """Analysis types."""

    intersects = "intersects"


# TODO: Differentiate the types here into import and export types?


# Rename to Vector tiles?


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

    @validator("extent", pre=True)
    def wkt_to_geojson(cls, v):
        if v and isinstance(v, WKBElement):
            return to_shape(v).__geo_interface__
        else:
            return v
    class Config:
        allow_population_by_field_name = True


class FeatureLayerCommonRead(FeatureLayerBase, ReadBase):
    content: Content
    style: Style | None
    data_store: DataStore | None


class LayerUpdateBase(ContentUpdate):
    """Base model for layer updates."""
    data_store_id: UUID | None
    data_source: str | None
    data_reference_year: int | None



################################################################################
# Table Layer DTOs
################################################################################

class TableLayerRead(LayerBase, ReadBase):
    content_id: UUID
    content: Content
    data_store: DataStore | None
class TableLayerUpdate(LayerUpdateBase):
    pass

################################################################################
# Feature Layer DTOs
################################################################################

class FeatureLayerStandardRead(FeatureLayerCommonRead):
    pass

class FeatureLayerStandardUpdate(LayerUpdateBase):
    pass


################################################################################
# Feature Layer Indicator  DTOs
################################################################################
class FeatureLayerIndicatorAttributesBase(BaseModel):
    """Base model for additional attributes feature layer indicator."""
    indicator_type: IndicatorType | None
    payload: dict | None 
    opportunities: list[UUID] | None 


class FeatureLayerIndicatorRead(FeatureLayerCommonRead, FeatureLayerIndicatorAttributesBase):
    """Model to read a feature layer indicator."""
    pass

################################################################################
# Feature Layer Scenario  DTOs
################################################################################

class FeatureLayerScenarioAttributesBase(BaseModel):
    """Base model for additional attributes feature layer indicator."""
    scenario_id: str | None
    scenario_type: ScenarioType | None
    scenario: Scenario | None

class FeatureLayerScenarioRead(FeatureLayerCommonRead, FeatureLayerScenarioAttributesBase):
    """Model to read a feature layer scenario."""
    pass

class FeatureLayerScenarioUpdate(FeatureLayerCommonRead):
    """Model to update a feature layer scenario."""

    pass

################################################################################
#  Imagery  Layer
################################################################################
class ImageryLayerAttributesBase(BaseModel):
    """Base model for additional attributes imagery layer."""
    url: str 
    data_type: ImageryLayerDataType 
    legend_urls: list[str] 

class ImageryLayerRead(LayerBase, ReadBase, ImageryLayerAttributesBase):
    """Model to read a imagery layer."""
    content: Content
    data_store: DataStore | None

################################################################################
# Tile  Layer  DTOs
################################################################################
class TileLayerAttributesBase(BaseModel):
    """Base model for additional attributes tile layer."""
    url: str 
    data_type: TileLayerDataType 

class TileLayerRead(LayerBase, ReadBase, TileLayerAttributesBase,):
    """Model to read a tile layer."""
    content: Content
    data_store: DataStore | None

################################################################################
################################################################################
################################################################################

def get_layer_class(class_type: str, **kwargs):
    layer_creator_class = {
        "table": TableLayerRead,
        "feature_layer": {
            "standard": FeatureLayerStandardRead,
            "indicator": FeatureLayerIndicatorRead,
            "scenario": FeatureLayerScenarioRead,
        },
        "imagery_layer": ImageryLayerRead,
        "tile_layer": TileLayerRead,

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

    if class_type == "update":
        layer_class_name = layer_class_name.replace("Read", "Update")

    elif class_type == "read":
        pass

    else:
        raise ValueError(f"Layer class type ({class_type}) is invalid")

    return globals()[layer_class_name]



class LayerRead(BaseModel):
    def __new__(cls, *args, **kwargs):
        layer_read_class = get_layer_class("read", **kwargs)
        return layer_read_class(**kwargs)



content_update_base_example = {
    "name": "Updated content name",
    "description": "Updated content description",
    "tags": ["updated", "allient", "allient"],
    "thumbnail_url": "https://updated-content-thumbnail-url.com",
}

layer_update_base_example = {
    "data_source": "data_source plan4better example",
    "data_reference_year": 2023,
    "extent": "MULTIPOLYGON(((0 0, 0 1, 1 1, 1 0, 0 0)), ((2 2, 2 3, 3 3, 3 2, 2 2)))",
    "user_id": "3d2e5991-741a-4d26-a456-932d61559bb8"
}

feature_layer_update_base_example = {
    "style_id": "59832b1c-b098-492d-93e0-2f8360fce755",
    "feature_layer_type": "standard",
    "size": 2500,
}

geospatial_attributes_update_example = {
    "min_zoom": 100,
    "max_zoom": 200,
}

imagery_layer_attributes_update_example = {
    "url": "https://allient.io",
    "data_type": "wms",
    "legend_urls": [
        "https://allient.io",
        "https://geodata.nationaalgeoregister.nl/luchtfoto/rgb/wms?request=GetLegendGraphic&service=WMS&layer=Actueel_ortho25&format=image/png&width=20&height=20",
    ],
    "type": "imagery_layer",
}


tile_layer_attributes_update_example = {
    "url": "https://allient.io",
    "data_type": "mvt",
    "type": "tile_layer",
}



request_examples_update = {
    "update": {
        "table_layer": {
            "summary": "Table Layer",
            "value": {
                **layer_update_base_example,
                **content_update_base_example,
            },
            "type": "table",
        },
        "layer_standard": {
            "summary": "Layer Standard",
            "value": {
                **content_update_base_example,
                **feature_layer_update_base_example,
                **geospatial_attributes_update_example,
                **layer_update_base_example,
            },
        },
        "imagery_layer": {
            "summary": "Imagery Layer",
            "value": {
                **content_update_base_example,
                **layer_update_base_example,
                **geospatial_attributes_update_example,
                **imagery_layer_attributes_update_example,
            },
        },
        "tile_layer": {
            "summary": "Tile Layer",
            "value": {
                **content_update_base_example,
                **layer_update_base_example,
                **geospatial_attributes_update_example,
                **tile_layer_attributes_update_example,
            },
        },
    },
}


request_examples = {
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
            },
        },
        "imagery_layer": {
            "summary": "Imagery Layer",
            "value": {
                **content_base_example,
                **layer_base_example,
                **geospatial_attributes_example,
                **imagery_layer_attributes_example,
            },
        },
        "tile_layer": {
            "summary": "Tile Layer",
            "value": {
                **content_base_example,
                **layer_base_example,
                **geospatial_attributes_example,
                **tile_layer_attributes_example,
            },
        },
    },
}

