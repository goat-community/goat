from typing import List

from geojson_pydantic.features import FeatureCollection
from pydantic import BaseModel

"""
Body of the request
"""


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


class ScenarioReadDeleted(ScenarioBase):
    layer_name: str

    class Config:
        schema_extra = {"example": {"scenario_id": 1, "layer_name": "pois"}}


class ScenarioUpdateDeleted(ScenarioBase):
    layer_name: str
    deleted_feature_ids: List[int]

    class Config:
        schema_extra = {
            "example": {"scenario_id": 1, "layer_name": "pois", "deleted_feature_ids": [1, 2, 3]}
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


class ScenarioCreate(BaseModel):
    user_id: int
    scenario_name: str

    class Config:
        schema_extra = {"example": {"scenario_name": "test", "user_id": 1}}


class ScenarioUpdate(ScenarioBase):
    scenario_name: str

    class Config:
        schema_extra = {"example": {"scenario_id": 1, "scenario_name": "test"}}
