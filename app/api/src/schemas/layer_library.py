from src.db import models


class CreateLayerLibrary(models.LayerLibrary):
    class Config:
        schema_extra = {
            "example": {
                "url": "https://{a-c}.basemaps.somecdn.com/dark_all/{z}/{x}/{y}.png",
                "legend_urls": "",
                "special_attribute": {"imagery_set": "Aerial"},
                "access_token": "some_token",
                "map_attribution": "Attribution to the source",
                "date": "",
                "source": "",
                "date_1": "",
                "source_1": "",
                "style_library_name": "",
                "max_resolution": "",
                "min_resolution": "",
                "id": 6,
                "name": "test",
                "type": "BING",
            }
        }
