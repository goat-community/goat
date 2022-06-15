from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from sqlmodel import SQLModel
from pydantic import Field


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
}
