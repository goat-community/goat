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
