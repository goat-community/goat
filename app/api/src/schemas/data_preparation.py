from pydantic import BaseModel

from .heatmap import HeatmapMode, HeatmapProfile
from .isochrone import IsochroneDTO


class BulkIdParameters(BaseModel):
    buffer_distance: int #in meters 
    study_area_ids: list[int]


class OpportunityMatrixParameters(BaseModel):
    bulk_id: str
    calculation_resolution: int
    isochrone_dto: IsochroneDTO

class OpportunityMatrixParameters2(BaseModel):
    bulk_id: list[str]
    calculation_resolution: int
    isochrone_dto: IsochroneDTO

class ConnectivityMatrixParameters(BaseModel):
    mode: str
    profile: str
    study_area_id: int
    max_time: int



ConnectivityMatrixExample = {
    "mode": "walking",
    "profile": "standard",
    "study_area_id": 91620000,
    "max_time": 20
}
class OpportunityMatrixOldParameters(BaseModel):
    calculation_resolution: int
    isochrone_dto: IsochroneDTO
    bulk_resolution: int
    calculation_resolution: int
    buffer_size: float
    speed: float
    travel_time: float
    study_area_ids: list[int]

class ConnectivityHeatmapParameters(BaseModel):
    mode: HeatmapMode
    profile: HeatmapProfile
    study_area_id: int
    max_travel_time: int
    
    
    

ConnectivityHeatmapParametersExample = {
    "mode": "walking",
    "profile": "standard",
    "study_area_id": 91620000,
    "max_travel_time": 20
}
    
    
    
BulkIdParametersExample = {
    "buffer_distance": 1000,
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
        