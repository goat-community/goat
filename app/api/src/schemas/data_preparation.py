from typing import Optional

from pydantic import BaseModel

from .heatmap import HeatmapMode, HeatmapProfile
from .isochrone import IsochroneDTO


class BulkIdParameters(BaseModel):
    buffer_distance: int  # in meters
    study_area_ids: list[int]


class OpportunityMatrixParameters(BaseModel):
    bulk_id: list[str]
    calculation_resolution: int
    isochrone_dto: IsochroneDTO
    s3_folder: Optional[str] = ""

class OpportunityMatrixParametersSingleBulk(OpportunityMatrixParameters):
    bulk_id: str


class ConnectivityMatrixParameters(BaseModel):
    mode: str
    profile: str
    study_area_id: int
    max_time: int


ConnectivityMatrixExample = {
    "mode": "walking",
    "profile": "standard",
    "study_area_id": 91620000,
    "max_time": 20,
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
    "max_travel_time": 20,
}


BulkIdParametersExample = {"buffer_distance": 1000, "study_area_ids": [91620000]}


OpportunityMatrixParametersExample = {
    "active_mobility": {
        "summary": "Opportunity Matrix for Active Mobility",
        "value": {
            "bulk_id": ["861f8d55fffffff"],
            "calculation_resolution": 10,
            "isochrone_dto": {
                "mode": "walking",
                "settings": {"travel_time": 20, "speed": 5, "walking_profile": "standard"},
                "starting_point": {"input": [{"lat": 48.1502132, "lon": 11.5696284}]},
                "scenario": {"id": 0, "modus": "default"},
                "output": {"type": "grid", "resolution": 12},
            },
            "s3_folder": "test",
        },
    },
    "motorized_transport": {
        "summary": "Opportunity Matrix for Motorized Transport (Public Transport or Car)",
        "value": {
            "bulk_id": ["861f8d55fffffff"],
            "calculation_resolution": 9,
            "isochrone_dto": {
                "mode": "transit",
                "settings": {
                    "travel_time": "60",
                    "transit_modes": ["bus", "tram", "subway", "rail"],
                    "weekday": "0",
                    "access_mode": "walk",
                    "egress_mode": "walk",
                    "bike_traffic_stress": 4,
                    "from_time": 25200,
                    "to_time": 39600,
                    "max_rides": 4,
                    "max_bike_time": 20,
                    "max_walk_time": 20,
                    "percentiles": [5, 25, 50, 75, 95],
                    "monte_carlo_draws": 200,
                },
                "starting_point": {"input": [{"lat": 48.1502132, "lon": 11.5696284}]},
                "scenario": {"id": 0, "modus": "default"},
                "output": {"type": "grid", "resolution": "9"},
            },
            "s3_folder": "test",
        },
    },
}
