from datetime import datetime
from typing import Optional
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
    accessGroup: str
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


class R5RegionInDB(R5Common):
    description: str
    bounds: R5Bounds


request_examples = {
    "region": {
        "create": {
            "name": "Freiburg",
            "description": "Demo - Freiburg Region for PT",
            "bounds": {"north": 48.11293, "south": 47.87214, "east": 8.06671, "west": 7.66296},
        }
    }
}
