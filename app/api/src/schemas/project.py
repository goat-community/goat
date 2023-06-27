
from uuid import UUID
from .report import ReportProject
from sqlmodel import Field
from pydantic import BaseModel, validator
from typing import Optional, List, Union, TYPE_CHECKING
from .layer import (
    # LayerProject,
    FeatureLayerAnalysisUnitProject,
    FeatureLayerIndicatorProject,
    FeatureLayerOpportunityProject,
    FeatureLayerStandardProject,
    TableLayerProject,
    TileLayerProject,
    ImageryLayerProject,
)
from enum import Enum
if TYPE_CHECKING:
    from .content import ContentBase, ContentUpdateBase

################################################################################
# Project DTOs
################################################################################
class ProjectContentType(str, Enum):
    """Content types that can be stored in a project."""

    layer = "layer"
    report = "report"
    style = "style"

class InitialViewState(BaseModel):
    """Model to show the initial view state of a project."""

    latitude: float = Field(
        ..., description="Latitude", ge=-90, le=90
    )
    longitude: float = Field(
        ..., description="Longitude", ge=-180, le=180
    )
    zoom: int = Field(
        ..., description="Zoom level", ge=0, le=20
    )
    min_zoom: int = Field(
        ..., description="Minimum zoom level", ge=0, le=20
    )
    max_zoom: int = Field(
        ..., description="Maximum zoom level", ge=0, le=20
    )
    bearing: int = Field(
        ..., description="Bearing", ge=0, le=360
    )
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


class ProjectAttributesBase(BaseModel):
    initial_view_state: InitialViewState = Field(
        ..., description="Initial view state of the project"
    )
    reports: Optional[List[ReportProject]] = Field(
        None, description="List of reports contained in the project"
    )
    layers: Optional[
        List[
            Union[
                FeatureLayerAnalysisUnitProject,
                FeatureLayerIndicatorProject,
                FeatureLayerOpportunityProject,
                FeatureLayerStandardProject,
                TableLayerProject,
                TileLayerProject,
                ImageryLayerProject,
            ]
        ]
    ] = Field(None, description="List of layers contained in the project")


class ProjectCreate(ContentBase, ProjectAttributesBase):
    pass


class ProjectRead(ContentBase, ProjectAttributesBase):
    id: UUID = Field(..., description="Project ID")


class ProjectUpdate(ContentUpdateBase):
    initial_view_state: Optional[InitialViewState] = Field(
        ..., description="Initial view state of the project"
    )
    reports: Optional[List[ReportProject]] = Field(
        None, description="List of reports contained in the project"
    )
    layers: Optional[
        List[
            Union[
                FeatureLayerAnalysisUnitProject,
                FeatureLayerIndicatorProject,
                FeatureLayerOpportunityProject,
                FeatureLayerStandardProject,
                TableLayerProject,
                TileLayerProject,
                ImageryLayerProject,
            ]
        ]
    ] = Field(None, description="List of layers contained in the project")



import uuid 
dummy_one_project = {
    "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "name": "My new project",
    "description": "My new project description",
    "thumbnail_url": "https://assets.plan4better.de/api/thumbnail/1.png",
    "tags": [
        "tag1",
        "tag2"
    ],
    "created_by": "majk.shkurti@plan4better.de",
    "updated_by": "elias.pajares@plan4better.de",
    "created_at": "2021-03-03T09:00:00.000000Z",
    "updated_at": "2021-03-03T09:00:00.000000Z",
    "shared_with": [
        {
            "group_id": 1,
            "group_name": "My Group 1",
            "image_url": "https://assets.plan4better.de/api/thumbnail/1.png"
        },
        {
            "group_id": 2,
            "group_name": "My Group 2",
            "image_url": "https://assets.plan4better.de/api/thumbnail/2.png"
        }
    ],
    "initial_view_state": {
        "latitude": 48.1502132,
        "longitude": 11.5696284,
        "zoom": 12,
        "min_zoom": 0,
        "max_zoom": 22,
        "bearing": 0,
        "pitch": 0
    },
    "reports": [
        {
            "id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p1",
            "name": "My new report 1",
            "description": "My new report description 1"
        }
    ],
    "layers": [
        {
            "id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p1",
            "type": "feature_layer",
            "feature_layer_type": "indicator",
            "data_type": "mvt",
            "name": "heatmap_connectivity",
            "group": "My Layers 1",
            "label": "My Connectivity Heatmap 1",
            "payload": {
                "mode": "walking",
                "study_area_ids": [
                    91620000
                ],
                "walking_profile": "standard",
                "scenario": {
                    "id": 1,
                    "name": "default"
                },
                "heatmap_type": "connectivity",
                "analysis_unit": "hexagon",
                "resolution": 9,
                "heatmap_config": {
                    "max_traveltime": 20
                }
            },
            "style_url": "https://assets.plan4better.de/api/style/1.json",
            "translation_urls": {
                "de": "https://assets.plan4better.de/api/translation/1_de.json",
                "en": "https://assets.plan4better.de/api/translation/1_en.json"
            },
            "created_at": "2021-03-03T09:00:00.000000Z",
            "updated_at": "2021-03-03T09:00:00.000000Z"
        },
        {
            "id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p2",
            "type": "feature_layer",
            "feature_layer_type": "indicator",
            "data_type": "binary",
            "name": "isochrone",
            "group": "My Layers 1",
            "label": "My new Isochrone Layer 1",
            "payload": {
                "mode": "walking",
                "settings": {
                    "travel_time": "10",
                    "speed": "5",
                    "walking_profile": "standard"
                },
                "starting_point": {
                    "input": [
                        {
                            "lat": 48.1502132,
                            "lon": 11.5696284
                        }
                    ]
                },
                "scenario": {
                    "id": 0,
                    "modus": "default"
                },
                "output": {
                    "type": "grid",
                    "resolution": "12"
                }
            },
            "opportunities": [
                {
                    "id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p3",
                    "query": "category=restaurant"
                }
            ],
            "style_url": "https://assets.plan4better.de/api/style/2.json",
            "translation_urls": {
                "de": "https://assets.plan4better.de/api/translation/2_de.json",
                "en": "https://assets.plan4better.de/api/translation/2_en.json"
            },
            "created_at": "2021-03-03T09:00:00.000000Z",
            "updated_at": "2021-03-03T09:00:00.000000Z"
        },
        {
            "id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p4",
            "type": "feature_layer",
            "feature_layer_type": "indicator",
            "data_type": "mvt",
            "name": "scenario_building",
            "group": "My Layers 1",
            "label": "My new Building Layer 1",
            "scenario_id": 10,
            "style_url": "https://assets.plan4better.de/api/style/3.json",
            "translation_urls": {
                "de": "https://assets.plan4better.de/api/translation/3_de.json",
                "en": "https://assets.plan4better.de/api/translation/3_en.json"
            },
            "created_at": "2021-03-03T09:00:00.000000Z",
            "updated_at": "2021-03-03T09:00:00.000000Z"
        },
        {
            "id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p5",
            "type": "scenario",
            "data_type": "geojson",
            "name": "scenario_ways",
            "group": "My Layers 1",
            "label": "My new street",
            "scenario_id": 10,
            "style_url": "https://assets.plan4better.de/api/style/4.json",
            "translation_urls": {
                "de": "https://assets.plan4better.de/api/translation/4_de.json",
                "en": "https://assets.plan4better.de/api/translation/4_en.json"
            },
            "created_at": "2021-03-03T09:00:00.000000Z",
            "updated_at": "2021-03-03T09:00:00.000000Z"
        },
        {
            "id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
            "type": "standard",
            "data_type": "wms",
            "name": "noise",
            "group": "My Layers 1",
            "label": "My new WMS",
            "url": "https://www.lfu.bayern.de/gdi/wms/laerm/ballungsraeume?LAYERS=aggroadlden",
            "legend_urls": [
                "https://ows.terrestris.de/osm/service?REQUEST=GetLegendGraphic&VERSION=1.0.0&FORMAT=image/png&WIDTH=20&HEIGHT=20&LAYER=OSM-WMS"
            ],
            "min_zoom": 0,
            "max_zoom": 22,
            "data_source": "Landesamt für Umwelt Bayern",
            "data_reference_year": "2021",
            "created_at": "2021-03-03T09:00:00.000000Z",
            "updated_at": "2021-03-03T09:00:00.000000Z"
        },
        {
            "id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p7",
            "type": "standard",
            "data_type": "geojson",
            "name": "starting_point",
            "group": "My Layers 1",
            "label": "Starting point",
            "style_url": "https://assets.plan4better.de/api/style/5.json",
            "translation_urls": {
                "de": "https://assets.plan4better.de/api/translation/5_de.json",
                "en": "https://assets.plan4better.de/api/translation/5_en.json"
            },
            "created_at": "2021-03-03T09:00:00.000000Z",
            "updated_at": "2021-03-03T09:00:00.000000Z"
        },
        {
            "id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p8",
            "type": "opportunity",
            "data_type": "mvt",
            "name": "building",
            "group": "My buildings",
            "label": "My new MVT",
            "scenario_id": 10,
            "opportunities": [
                {
                    "id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p10",
                    "query": "area>50"
                }
            ],
            "url": "https://tiles.plan4better.de/api/building/{z}/{x}/{y}.pbf",
            "min_zoom": 0,
            "max_zoom": 22,
            "style_url": "https://assets.plan4better.de/api/style/5.json",
            "translation_urls": {
                "de": "https://assets.plan4better.de/api/translation/5_de.json",
                "en": "https://assets.plan4better.de/api/translation/5_en.json"
            },
            "created_at": "2021-03-03T09:00:00.000000Z",
            "updated_at": "2021-03-03T09:00:00.000000Z"
        },
        {
            "id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p9",
            "type": "opportunity",
            "data_type": "mvt",
            "name": "poi",
            "group": "My Layers 1",
            "label": "My new POI Layer 1",
            "scenario_id": 10,
            "opportunities": [
                {
                    "id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p10",
                    "query": "category=restaurant,bar"
                }
            ],
            "active_opportunities": [
                {
                    "id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p10",
                    "query": "category=restaurant"
                }
            ],
            "url": "https://tiles.plan4better.de/api/poi/{z}/{x}/{y}.pbf",
            "style_url": "https://assets.plan4better.de/api/style/5.json",
            "translation_urls": {
                "de": "https://assets.plan4better.de/api/translation/5_de.json",
                "en": "https://assets.plan4better.de/api/translation/5_en.json"
            },
            "created_at": "2021-03-03T09:00:00.000000Z",
            "updated_at": "2021-03-03T09:00:00.000000Z"
        }
    ]
}

# Create projects list with different ids that are uuids
dummy_projects = []
uuids = [
    uuid.UUID('d243947f-2417-4e4b-a5e9-5a9c3f8e8211'),
    uuid.UUID('3d54bce4-9e0f-4360-86f2-8dd02b51b3e8'),
    uuid.UUID('e27a1bf5-4f64-4a2b-b1e6-f8940845be3c'),
    uuid.UUID('b4de6b49-8d79-43c8-a6c0-9271f6c06f5b'),
    uuid.UUID('a981d56c-50b7-4c12-b2a3-1e0d8d89ff7d')
]

for i in uuids:
    project_copy = dummy_one_project.copy()
    project_copy["id"] = i 
    project_copy["name"] = "My new project " + str(i)
    project_copy["description"] = "My new project description " + str(i)
    dummy_projects.append(project_copy)
    