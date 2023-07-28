
from pydantic import BaseModel, Field, ValidationError, validator





def get_layer_class(class_type: str, **kwargs):

    layer_creator_class = {
        "table": TableLayerCreate,
        "tile_layer": TileLayerCreate,
        "imagery_layer": ImageryLayerCreate,
        "feature_layer": {
            "standard": IFeatureLayerStandardCreate,
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



class LayerRead(BaseModel):
    def __new__(cls, *args, **kwargs):
        layer_read_class = get_layer_class("read", **kwargs)
        return layer_read_class(**kwargs)
