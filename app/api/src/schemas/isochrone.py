from enum import Enum, IntEnum
from typing import Dict, List, Optional, Union

from geojson_pydantic.features import Feature, FeatureCollection
from geojson_pydantic.geometries import MultiPolygon, Polygon
from pydantic import BaseModel, root_validator

"""
Body of the request
"""


# class ModusEnum(int, Enum):
#     default = 1
#     scenario = 2
#     comparision = 3

#     @classmethod
#     def __get_validators__(cls):
#         cls.lookup = {v: k.value for v, k in cls.__members__.items()}
#         yield cls.validate

#     @classmethod
#     def validate(cls, v):
#         try:
#             return cls.lookup[v]
#         except KeyError:
#             raise ValueError("invalid modus value")


class IsochroneTypeEnum(str, Enum):
    single = "single_isochrone"
    multi = "multi_isochrone"


class IsochroneBase(BaseModel):
    user_id: int
    scenario_id: Optional[int] = 0
    minutes: int
    speed: float
    modus: str
    n: int
    routing_profile: str
    active_upload_ids: Optional[List[int]] = [0]

    @root_validator
    def compute_values(cls, values):
        """Compute values."""
        # convert speed from km/h to m/s
        values["speed"] = values["speed"] / 3.6
        # convert minutes to seconds (max_cutoff is in seconds)
        values["max_cutoff"] = values["minutes"] * 60
        return values


class IsochroneSingle(IsochroneBase):
    x: float
    y: float

class IsochroneMulti(IsochroneBase):
    x: list[float]
    y: list[float]

class IsochronePoiMulti(IsochroneBase):
    region_type: str
    region: List[str]
    scenario_id: int
    amenities: List[str]

    @root_validator
    def define_study_area_ids(cls, values):
        if values["region_type"] == "study_area":
            values["study_area_ids"] = [int(integer_string) for integer_string in values["region"]]
            values["region"] = None
        elif values["region_type"] == "polygon":
            values["study_area_ids"] = None 
        else: 
            raise ValueError("Invalid region type")
        return values

class IsochroneMultiCountPois(BaseModel):
    user_id: int
    scenario_id: Optional[int] = 0
    amenities: List[str]
    minutes: int
    modus: str
    region: str
    region_type: str
    speed: int
    active_upload_ids: Optional[List[int]] = [0]


class IsochroneExport(BaseModel):
    """Isochrone export DTO"""

    return_type: str
    objectid: int


class IsochroneExport(BaseModel):
    """Isochrone export DTO"""
    return_type: str
    objectid: int


"""
Response DTOs
"""

# Shared properties
class IsochronePropertiesShared(BaseModel):
    gid: int
    step: int
    modus: int
    speed: int
    objectid: int
    parent_id: int
    coordinates: List


class IsochroneSingleProperties(IsochronePropertiesShared):
    starting_point: str
    sum_pois: Dict


# Single Isochrone
class IsochroneSingleFeature(Feature):
    geometry: Union[Polygon, MultiPolygon]
    properties: IsochroneSingleProperties


class IsochroneSingleCollection(FeatureCollection):
    features: List[IsochroneSingleFeature]


# Multi Isochrone
class IsochroneMultiProperties(IsochronePropertiesShared):
    userid: str
    population: List
    scenario_id: int
    routing_profile: str
    alphashape_parameter: str


class IsochroneMultiFeature(Feature):
    geometry: Union[Polygon, MultiPolygon]
    properties: IsochroneMultiProperties


class IsochroneMultiCollection(FeatureCollection):
    features: List[IsochroneMultiFeature]


# Count pois (multi-isochrone) TODO: THERE IS NO NEED IN THE CLIENT TO HAVE THIS AS FEATURE COLLECTION


class IsochroneMultiCountPoisProperties(BaseModel):
    gid: int
    count_pois: int
    region_name: str


class IsochroneMultiCountPoisFeature(Feature):
    geometry: Union[Polygon, MultiPolygon]
    properties: IsochroneMultiCountPoisProperties


class IsochroneMultiCountPoisCollection(FeatureCollection):
    features: List[IsochroneMultiCountPoisFeature]


request_examples = {
    "single_isochrone": {
        "user_id": 1,
        "minutes": 10,
        "speed": 5,
        "n": 2,
        "modus": "default",
        "x": 11.5696284,
        "y": 48.1502132,
        "routing_profile": "walking_standard",
        "active_upload_ids": [0],
        "scenario_id": 0
    },
    "multi_isochrone": {
        "user_id": 1,
        "minutes": 10,
        "speed": 5,
        "n": 2,
        "modus": "default",
        "x": [11.5696284, 11.573464],
        "y": [48.1502132, 48.153734],
        "routing_profile": "walking_standard",
        "active_upload_ids": [0],
        "scenario_id": 0    
    },
    "pois_multi_isochrone_study_area": {
        "multi_with_study_area": {
            "summary": "Multi Isochrone with Study Area",
            "value": {
                "user_id": 1,
                "minutes": 10,
                "speed": 5,
                "n": 2,
                "modus": "default",
                "region_type": "study_area",
                "region": ["1", "2", "3"],
                "routing_profile": "walking_standard",
                "active_upload_ids": [0],
                "scenario_id": 0,
                "amenities": [
                    "nursery",
                    "kindergarten",
                    "grundschule",
                    "realschule",
                    "werkrealschule",
                    "gymnasium",
                    "library",
                ],
            }
        },
        "multi_with_polygon": {
            "summary": "Multi Isochrone with Polygon",
            "value": {
                "user_id": 1261,
                "minutes": 10,
                "speed": 5,
                "n": 2,
                "modus": "default",
                "region_type": "draw",
                "region": [
                    "POLYGON((11.53605224646383 48.15855242757948,11.546141990292947 48.16035646918763,11.54836104048217 48.15434275044706,11.535497483916524 48.15080357881183,11.526586610500429 48.15300113241156,11.531302092152526 48.15799732509075,11.53605224646383 48.15855242757948))"
                ],
                "routing_profile": "walking_standard",
                "scenario_id": 0,
                "amenities": [
                    "nursery",
                    "kindergarten"
                ],
                "scenario_id": 0,
                "active_upload_ids": [0]
            }
        }
    },
    "pois_multi_isochrone_count_pois": {
        "region_type": "draw",
        "region": "POLYGON((11.53605224646383 48.15855242757948,11.546141990292947 48.16035646918763,11.54836104048217 48.15434275044706,11.535497483916524 48.15080357881183,11.526586610500429 48.15300113241156,11.531302092152526 48.15799732509075,11.53605224646383 48.15855242757948))",
        "user_id": 1,
        "scenario_id": 0,
        "modus": "default",
        "routing_profile": "walking_standard",
        "minutes": 10,
        "speed": 5,
        "amenities": [
            "kindergarten",
            "grundschule",
            "hauptschule_mittelschule",
            "realschule",
            "gymnasium",
            "library",
        ],
    },
    
}