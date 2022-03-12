from enum import Enum
from typing import Dict, List, Union

from geojson_pydantic.features import FeatureCollection
from pydantic import BaseModel

from src.db.models import population


class ScenarioBase(BaseModel):
    scenario_id: int


class ScenarioImport(ScenarioBase):
    user_id: int
    layer_name: str
    payload: FeatureCollection

    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "scenario_id": 6,
                "layer_name": "ways",
                "payload": {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "geometry": {
                                "type": "LineString",
                                "coordinates": [
                                    [7.850605211, 47.995588854000005],
                                    [7.850990133, 47.99593471899999],
                                    [7.851685883999999, 47.99564569199998],
                                ],
                            },
                            "properties": {
                                "lit": "null",
                                "foot": "null",
                                "bicycle": "null",
                                "surface": "asphalt",
                                "way_type": "bridge",
                                "edit_type": "new",
                                "wheelchair": "yes",
                                "original_id": "null",
                                "street_category": "null",
                            },
                            "id": 1,
                        }
                    ],
                },
            }
        }


class ScenarioDelete(ScenarioBase):
    layer_name: str
    deleted_feature_ids: List[int]
    drew_fid: int

    class Config:
        schema_extra = {
            "example": {
                "scenario_id": 1,
                "layer_name": "pois",
                "deleted_feature_ids": [1, 2, 3],
                "drew_fid": 14,
            }
        }


# -----------------------------------------------------------------------------
class ScenarioLayersEnum(Enum):
    """Scenario Layers Enums."""

    ways = "ways"
    pois = "pois"
    buildings = "buildings"


class ScenarioLayerFeatureEnum(Enum):
    """Scenario Layer Feature Delete Enums."""

    way_modified = "way_modified"
    poi_modified = "poi_modified"
    building_modified = "building_modified"
    population_modified = "population_modified"


class ScenarioLayersNoPoisEnum(Enum):
    """Scenario Layers without POIS."""

    edge = "edge"
    way_modified = "way_modified"
    building = "building"
    building_modified = "building_modified"
    population = "population"
    population_modified = "population_modified"


class ScenarioCreate(BaseModel):
    scenario_name: str


class ScenarioUpdate(BaseModel):
    scenario_name: str


class ScenarioFeatureCreate(BaseModel):
    features: List[Dict]


"""
Body of the request
"""
request_examples = {
    "create": {"scenario_name": "test"},
    "update": {"scenario_name": "test_updated"},
    "update_deleted_features": [1, 2, 3],
    "read_features": {
        "scenario_id": 1,
        "layer_name": "edge",
        "intersect": "POLYGON((11.55947247425152 48.15680551331815,11.559310821465383 48.15790039566741,11.558832075332894 48.15895318026625,11.558054633799436 48.159923412979424,11.557008373507147 48.16077381397483,11.555733501652313 48.161471709503445,11.554279010845356 48.161990286516016,11.552700796352298 48.162309622055574,11.551059508071036 48.162417448022694,11.549418219789775 48.162309622055574,11.547840005296717 48.161990286516016,11.546385514489758 48.161471709503445,11.545110642634924 48.16077381397483,11.544064382342636 48.159923412979424,11.543286940809178 48.15895318026625,11.54280819467669 48.15790039566741,11.542646541890553 48.15680551331815,11.54280819467669 48.155710607603396,11.543286940809178 48.15465775646527,11.544064382342636 48.153687424168936,11.545110642634924 48.15283690570729,11.546385514489758 48.152138892712344,11.547840005296717 48.15162021611667,11.549418219789775 48.151300814037825,11.551059508071036 48.15119296470522,11.552700796352298 48.151300814037825,11.554279010845356 48.15162021611667,11.555733501652313 48.152138892712344,11.557008373507147 48.15283690570729,11.558054633799436 48.153687424168936,11.558832075332894 48.15465775646527,11.559310821465383 48.155710607603396,11.55947247425152 48.15680551331815))",
    },
    "delete_feature": {
        "scenario_id": 1,
        "layer_name": "way_modified",
        "feature_id": 1,
    },
    "create_feature": {
        "scenario_id": 1,
        "layer_name": "way_modified",
        "payload": {
            "features": [
                {
                    "scenario_id": 12,
                    "original_id": None,
                    "class_id": 113,
                    "way_type": "bridge",
                    "surface": "asphalt",
                    "wheelchair": "yes",
                    "lit": None,
                    "geom": "LINESTRING(11.510148251443228 48.1643284471769,11.5112867863764 48.1634171605524,11.513123622735256 48.16285012959281,11.515264068409625 48.162475480698475,11.515598038656687 48.16323490128468,11.516660671260983 48.163862680480435)",
                }
            ]
        },
    },
}
