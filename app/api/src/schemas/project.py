from enum import Enum
from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, validator

from .layer import (
    IFeatureLayerIndicatorRead,
    IFeatureLayerStandardRead,
    IImageryLayerRead,
    ITableLayerRead,
    ITileLayerRead,
    content_base_example,
    request_examples as layer_request_examples,
)
from src.db.models.layer import ContentBaseAttributes
from src.db.models.project import Project
from .report import IReportRead
from src.schemas.report import request_examples as report_request_examples


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
    "max_zoom": 22,
    "bearing": 0,
    "pitch": 0,
}


class IProjectAttributesBase(BaseModel):
    initial_view_state: InitialViewState = Field(
        ..., description="Initial view state of the project"
    )
    reports: List[dict] | None = Field(
        None, description="List of reports contained in the project"
    )
    layers: List[
        Union[
            IFeatureLayerIndicatorRead,
            IFeatureLayerStandardRead,
            ITableLayerRead,
            ITileLayerRead,
            IImageryLayerRead,
        ]
    ] | None = Field(None, description="List of layers contained in the project")


class IProjectCreate(ContentBaseAttributes):
    pass


class IProjectRead(ContentBaseAttributes):
    id: UUID = Field(..., description="Project ID")
    reports: List[dict] | None = Field([], description="List of reports contained in the project")
    layers: List[
        Union[
            IFeatureLayerIndicatorRead,
            IFeatureLayerStandardRead,
            ITableLayerRead,
            ITileLayerRead,
            IImageryLayerRead,
        ]
    ] | None = Field([], description="List of layers contained in the project")


class IProjectUpdate(ContentBaseAttributes):
    pass


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
    },
}
