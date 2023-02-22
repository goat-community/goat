from pydantic import BaseModel

from .isochrone import IsochroneDTO


class BulkIdParameters(BaseModel):
    bulk_resolution: int
    calculation_resolution: int
    speed: float
    travel_time: float
    study_area_ids: list[int]


class OpportunityMatrixParameters(BaseModel):
    bulk_id: str
    calculation_resolution: int
    isochrone_dto: IsochroneDTO

class OpportunityMatrixParameters2(BaseModel):
    bulk_id: list[str]
    calculation_resolution: int
    isochrone_dto: IsochroneDTO
    
    
    
    
BulkIdParametersExample = {
    "bulk_resolution": 6,
    "calculation_resolution": 10,
    "speed": 5,
    "travel_time": 20,
    "study_area_ids": [91620000]
}

OpportunityMatrixParametersExample = {
    "bulk_id": ["861f8d55fffffff"],
    "calculation_resolution": 10,
    "isochrone_dto": {
        "mode": "walking",
        "settings": {
            "travel_time": 20,
            "speed": 5,
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
            "resolution": 12
        }
        }
}
        