from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from pydantic import Field
from sqlmodel import SQLModel

from src.resources.enums import R5DecayFunctionType


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class R5Common(SQLModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    accessGroup: Optional[str] = "local"
    nonce: str
    name: str
    createdAt: datetime
    createdBy: Optional[str] = "local"
    updatedAt: datetime
    updatedBy: Optional[str] = "local"

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class R5Bounds(SQLModel):
    north: float
    south: float
    east: float
    west: float


class R5RegionCreateDTO(SQLModel):
    bounds: R5Bounds
    name: str
    description: str


class R5ProjectCreateDTO(SQLModel):
    variants: List[str]
    regionId: str
    bundleId: str
    name: str


class R5RegionUpdateDTO(SQLModel):
    name: str
    description: str


class R5ProjectUpdateDTO(SQLModel):
    id: str
    name: str


class R5RegionInDB(R5Common):
    description: str
    bounds: R5Bounds


class R5ProjectInDB(R5Common):
    variants: List[str]
    regionId: str
    bundleId: str


class R5DecayFunction(SQLModel):
    type: Optional[R5DecayFunctionType] = R5DecayFunctionType.logistic
    standardDeviationMinutes: Optional[int] = 12
    widthMinutes: Optional[int] = 10


class R5IsochroneAnalysisDTO(SQLModel):
    accessModes: str
    bikeSpeed: Optional[float]
    bikeTrafficStress: Optional[int]
    date: Optional[str] = "2022-05-31"
    decayFunction: R5DecayFunction
    destinationPointSetIds: Optional[List[str]] = []
    directModes: Optional[str] = "WALK"
    egressModes: Optional[str] = "WALK"
    fromLat: float
    fromLon: float
    fromTime: int
    toTime: int
    zoom: Optional[int] = 10
    maxBikeTime: Optional[int] = 20  # minutes
    maxRides: Optional[int] = 4
    maxWalkTime: Optional[int] = 20  # minutes
    walkSpeed: Optional[float] = 1.3888888888888888  # m/s
    monteCarloDraws: Optional[int] = 200
    percentiles: Optional[List[int]] = [5, 25, 50, 75, 95]
    transitModes: Optional[str]
    variantIndex: Optional[int] = -1
    workerVersion: Optional[str] = "v6.4"
    # projectId: "6294f0ae0cfee1c6747d696c" ===> IS SET FROM STUDY ARE ON THE FLY #TODO:
    # bounds: R5Bounds ===> ARE SET FROM STUDY ARE ON THE FLY #TODO:


request_examples = {
    "region": {
        "create": {
            "name": "Freiburg",
            "description": "Demo - Freiburg Region for PT",
            "bounds": {"north": 48.11293, "south": 47.87214, "east": 8.06671, "west": 7.66296},
        },
        "update": {"name": "Freiburg", "description": "Demo - Freiburg Region for PT (UPDATE)"},
    },
    "bundle": {
        "create": {
            "bundleName": "Demo Bundle",
            "osm": "",
            "feedGroup": "",  # binary
            "regionId": "5e8f8f8f8f8f8f8f8f8f8f8",
        }
    },
    "project": {
        "create": {
            "name": "Demo Project",
            "bundleId": "5e8f8f8f8f8f8f8f8f8f8f8",
            "regionId": "5e8f8f8f8f8f8f8f8f8f8f8",
            "variants": ["Default"],
        },
        "update": {
            "name": "Demo Project (UPDATE)",
        },
    },
    "analysis": {
        "accessModes": "WALK",
        "bikeSpeed": 4.166666666666667,
        "bikeTrafficStress": 4,
        "date": "2022-06-10",
        "decayFunction": {
            "type": "logistic",
            "standardDeviationMinutes": 12,
            "widthMinutes": 10,
        },
        "destinationPointSetIds": [],
        "directModes": "WALK",
        "egressModes": "WALK",
        "fromLat": 48.11724008376831,
        "fromLon": 11.54651520171336,
        "fromTime": 25200,
        "toTime": 39600,
        "zoom": 9,
        "maxBikeTime": 20,
        "maxRides": 4,
        "maxWalkTime": 20,
        "monteCarloDraws": 200,
        "percentiles": [5, 25, 50, 75, 95],
        "transitModes": "BUS,TRAM,SUBWAY,RAIL",
        "variantIndex": -1,
        "walkSpeed": 1.3888888888888888,
        "workerVersion": "v6.4",
    },
}
