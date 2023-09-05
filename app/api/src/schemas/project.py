from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, validator

from src.db.models.layer import ContentBaseAttributes
from src.db.models._base_class import DateTimeBase
from src.utils import optional
from src.schemas.layer import (
    IFeatureLayerStandardRead,
    IFeatureLayerIndicatorRead,
    IFeatureLayerScenarioRead,
    ITableLayerRead,
    ITileLayerRead,
    IImageryLayerRead,
)


################################################################################
# Project DTOs
################################################################################
class ProjectContentType(str, Enum):
    layer = "layer"
    report = "report"


class InitialViewState(BaseModel):
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


initial_view_state_example = {
    "latitude": 48.1502132,
    "longitude": 11.5696284,
    "zoom": 12,
    "min_zoom": 0,
    "max_zoom": 20,
    "bearing": 0,
    "pitch": 0,
}


class IProjectCreate(ContentBaseAttributes):
    initial_view_state: InitialViewState = Field(
        ..., description="Initial view state of the project"
    )


class IProjectRead(ContentBaseAttributes, DateTimeBase):
    id: UUID = Field(..., description="Project ID")


@optional
class IProjectBaseUpdate(ContentBaseAttributes):
    pass


# Define layers within project


class IFeatureLayerBaseProject(BaseModel):
    name: str = Field(..., description="Layer name")
    group: str | None = Field(None, description="Layer group name")
    query: dict | None = Field(None, description="CQL2-JSON filter to query the layer")
    style: dict = Field(
        ...,
        description="Style of the layer",
    )


class IFeatureLayerStandardProjectRead(IFeatureLayerStandardRead, IFeatureLayerBaseProject):
    pass


class IFeatureLayerIndicatorProjectRead(IFeatureLayerIndicatorRead, IFeatureLayerBaseProject):
    pass


class IFeatureLayerScenarioProjectRead(IFeatureLayerScenarioRead, IFeatureLayerBaseProject):
    pass


class IFeatureLayerStandardProjectUpdate(IFeatureLayerBaseProject):
    pass

class IFeatureLayerIndicatorProjectUpdate(IFeatureLayerBaseProject):
    pass

class IFeatureLayerScenarioProjectUpdate(IFeatureLayerBaseProject):
    pass

class ITableLayerProjectRead(ITableLayerRead):
    group: str = Field(None, description="Layer group name")
    query: dict | None = Field(None, description="CQL2-JSON filter to query the layer")


class ITableLayerProjectUpdate(BaseModel):
    name: str | None = Field(None, description="Layer name")
    group: str | None = Field(None, description="Layer group name")
    query: dict | None = Field(None, description="CQL2-JSON filter to query the layer")


class ITileLayerProjectRead(ITileLayerRead):
    group: str = Field(None, description="Layer group name")


class ITileLayerProjectUpdate(BaseModel):
    name: str | None = Field(None, description="Layer name")
    group: str | None = Field(None, description="Layer group name")


class IImageryLayerProjectRead(IImageryLayerRead):
    group: str = Field(None, description="Layer group name")


class IImageryLayerProjectUpdate(BaseModel):
    name: str | None = Field(None, description="Layer name")
    group: str | None = Field(None, description="Layer group name")


layer_type_mapping_read = {
    "feature_layer_standard": IFeatureLayerStandardProjectRead,
    "feature_layer_indicator": IFeatureLayerIndicatorProjectRead,
    "feature_layer_scenario": IFeatureLayerScenarioProjectRead,
    "table_layer": ITableLayerProjectRead,
    "tile_layer": ITileLayerProjectRead,
    "imagery_layer": IImageryLayerProjectRead,
}

layer_type_mapping_update = {
    "feature_layer_standard": IFeatureLayerStandardProjectUpdate,
    "feature_layer_indicator": IFeatureLayerIndicatorProjectUpdate,
    "feature_layer_scenario": IFeatureLayerScenarioProjectUpdate,
    "table_layer": ITableLayerProjectUpdate,
    "tile_layer": ITileLayerProjectUpdate,
    "imagery_layer": IImageryLayerProjectUpdate,
}

request_examples = {
    "get": {
        "ids": ["39e16c27-2b03-498e-8ccc-68e798c64b8d", "e7dcaae4-1750-49b7-89a5-9510bf2761ad"],
    },
    "create": {
        "folder_id": "39e16c27-2b03-498e-8ccc-68e798c64b8d",
        "name": "Project 1",
        "description": "Project 1 description",
        "tags": ["tag1", "tag2"],
        "thumbnail_url": "https://goat-app-assets.s3.eu-central-1.amazonaws.com/logos/goat_green.png",
        "initial_view_state": initial_view_state_example,
    },
    "update": {
        "folder_id": "39e16c27-2b03-498e-8ccc-68e798c64b8d",
        "name": "Project 2",
        "description": "Project 2 description",
        "tags": ["tag1", "tag2"],
        "thumbnail_url": "https://goat-app-assets.s3.eu-central-1.amazonaws.com/logos/goat_green.png",
    },
    "initial_view_state": initial_view_state_example,
    "update_layer": {
        "feature_layer_standard": {
            "summary": "Feature Layer Standard",
            "value": {
                "name": "Feature Layer Standard",
                "group": "Group 1",
                "query": {},
                "style": {
                    "type": "circle",
                    "paint": {
                        "circle-radius": 5,
                        "circle-color": "#ff0000",
                    },
                },
            },
        },
        "feature_layer_indicator": {
            "summary": "Feature Layer Indicator",
            "value": {
                "name": "Feature Layer Indicator",
                "group": "Group 1",
                "query": {},
                "style": {
                    "type": "circle",
                    "paint": {
                        "circle-radius": 5,
                        "circle-color": "#ff0000",
                    },
                },
            },
        },
        "feature_layer_scenario": {
            "summary": "Feature Layer Scenario",
            "value": {
                "name": "Feature Layer Scenario",
                "group": "Group 1",
                "query": {},
                "style": {
                    "type": "circle",
                    "paint": {
                        "circle-radius": 5,
                        "circle-color": "#ff0000",
                    },
                },
            },
        },
        "table_layer": {
            "summary": "Table Layer",
            "value": {
                "name": "Table Layer",
                "group": "Group 1",
                "query": {},
            },
        },
        "tile_layer": {
            "summary": "Tile Layer",
            "value": {
                "name": "Tile Layer",
                "group": "Group 1",
            },
        },
        "imagery_layer": {
            "summary": "Imagery Layer",
            "value": {
                "name": "Imagery Layer",
                "group": "Group 1",
            },
        },
    },
}
