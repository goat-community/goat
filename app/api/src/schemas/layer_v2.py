
from pydantic import BaseModel, Field, ValidationError, validator
from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape
from uuid import UUID
from src.db.models.style import Style
from src.db.models.layer import IndicatorType
from src.schemas.content import ContentUpdate
from src.db.models.content import Content
from src.db.models.layer import LayerBase, FeatureLayerBase
from src.db.models.data_store import DataStore


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

class TableLayerCreate(LayerBase):
    pass

class TableLayerRead(LayerBase, ReadBase):
    content: Content

class TableLayerUpdate(LayerUpdateBase):
    pass

################################################################################
# Feature Layer DTOs
################################################################################

class FeatureLayerStandardCreate(LayerBase):
    pass

class FeatureLayerStandardRead(FeatureLayerCommonRead):
    pass

class FeatureLayerStandardUpdate(LayerUpdateBase):
    pass


################################################################################
# Feature Layer Indicator  DTOs
################################################################################
class FeatureLayerIndicatorAttributesBase(BaseModel):
    """Base model for additional attributes feature layer indicator."""
    indicator_type: IndicatorType 
    payload: dict | None 
    opportunities: list[UUID] | None 

class FeatureLayerIndicatorCreate(FeatureLayerCommonRead, FeatureLayerIndicatorAttributesBase):
    """Model to create feature layer indicator."""
    pass

class FeatureLayerIndicatorRead(FeatureLayerCommonRead, FeatureLayerIndicatorAttributesBase):
    """Model to read a feature layer indicator."""
    content: Content

def get_layer_class(class_type: str, **kwargs):

    layer_creator_class = {
        "table": TableLayerCreate,
        "feature_layer": {
            "standard": FeatureLayerStandardCreate,
            "indicator": FeatureLayerIndicatorCreate,
            # "scenario": FeatureLayerScenarioCreate,
        },
        # "tile_layer": TileLayerCreate,
        # "imagery_layer": ImageryLayerCreate,

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



class LayerRead(BaseModel):
    def __new__(cls, *args, **kwargs):
        layer_read_class = get_layer_class("read", **kwargs)
        return layer_read_class(**kwargs)
