
from pydantic import BaseModel, Field, ValidationError, validator
from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape
from uuid import UUID
from src.schemas.content import ContentUpdate
from src.db.models.content import Content
from src.db.models.layer import LayerBase


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
    class Config:
        allow_population_by_field_name = True



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



def get_layer_class(class_type: str, **kwargs):

    layer_creator_class = {
        "table": TableLayerCreate,
        # "feature_layer": {
        #     "standard": IFeatureLayerStandardCreate,
        #     "indicator": FeatureLayerIndicatorCreate,
        #     "scenario": FeatureLayerScenarioCreate,
        # },
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
