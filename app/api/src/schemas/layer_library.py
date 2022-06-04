from src.db import models
from pydantic import root_validator
from src.tests.utils.utils import random_lower_string
from datetime import datetime


def single_layer_library():
    return {
        "url": "https://{a-c}.basemaps.somecdn.com/dark_all/{z}/{x}/{y}.png",
        "legend_urls": [random_lower_string()],
        "special_attribute": {"imagery_set": "Aerial"},
        "access_token": "some_token",
        "map_attribution": "Attribution to the source",
        "date": str(datetime.today().year),
        "source": None,
        "date_1": str(datetime.today().year),
        "source_1": None,
        "style_library_name": None,
        "max_resolution": "0",
        "min_resolution": "0",
        "name": random_lower_string(),
        "type": "BING",
    }


request_examples = {"single_layer_library": single_layer_library}


class CreateLayerLibrary(models.LayerLibrary):
    @root_validator
    def urls_emptiness_vs_type(cls, values):
        # according to the issue: https://github.com/goat-community/goat/issues/1328
        url, the_type = values.get("url"), values.get("type")
        url_mandatory_types = ("WMS", "OSM", "BING")
        if the_type in url_mandatory_types and not url:
            raise ValueError("url should not be empty for the layer type %s." % the_type)

        return values

    @root_validator
    def legend_urls_emptiness_vs_type(cls, values):
        # according to the issue: https://github.com/goat-community/goat/issues/1328
        legend_urls, the_type = values.get("legend_urls"), values.get("type")
        legend_url_mandatory_types = ("WMS",)
        if the_type in legend_url_mandatory_types and not legend_urls:
            raise ValueError("legend_urls should not be empty for the layer type %s." % the_type)

        return values

    @root_validator
    def style_library_name_emptiness_vs_type(cls, values):
        # according to the issue: https://github.com/goat-community/goat/issues/1328
        style_library_name, the_type = values.get("style_library_name"), values.get("type")
        legend_url_mandatory_types = ("MVT", "GEOBUF", "WFS")
        if the_type in legend_url_mandatory_types and not style_library_name:
            raise ValueError(
                "style_library_name should not be empty for the layer type %s." % the_type
            )

        return values

    class Config:
        schema_extra = {"example": request_examples["single_layer_library"]()}
