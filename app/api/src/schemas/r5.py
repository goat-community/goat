from typing import List
from sqlmodel import SQLModel

class R5Bounds(SQLModel):
    north: float
    south: float
    east: float
    west: float

class R5ProjectCreate(SQLModel):
    name: str
    description: str
    bounds: R5Bounds





request_examples = {
    "create": {
        "name": "Freiburg",
        "description": "Demo - Freiburg Region for PT",
        "bounds": {"north": 48.11293, "south": 47.87214, "east": 8.06671, "west": 7.66296},
    }
}
