from typing import Optional

from pydantic import BaseModel, Field

from .heatmap import HeatmapMode, HeatmapProfile
from .isochrone import (
    IsochroneAccessMode,
    IsochroneDTO,
    IsochroneMode,
    IsochroneOutput,
    IsochroneSettings,
)


class HeatmapIsochroneDTO(BaseModel):
    mode: IsochroneMode = Field(IsochroneAccessMode.WALK, description="Isochrone Mode")
    settings: IsochroneSettings = Field(..., description="Isochrone settings parameters")
    output: Optional[IsochroneOutput] = Field(..., description="Isochrone output parameters")


class BulkIdParameters(BaseModel):
    buffer_distance: int  # in meters
    study_area_ids: list[int]


class TravelTimeMatrixParameters(BaseModel):
    bulk_id: list[str]
    isochrone_dto: IsochroneDTO
    calculation_resolution: int
    s3_folder: Optional[str] = ""


class TravelTimeMatrixParametersSingleBulk(TravelTimeMatrixParameters):
    bulk_id: str


class OpportunityMatrixParameters(TravelTimeMatrixParameters):
    opportunity_types: Optional[list[str]] = ["population", "aoi", "poi"]
    scenario_ids: Optional[list[int]] = []
    user_data_ids: Optional[list[int]] = []
    compute_base_data: Optional[bool] = True


class OpportunityMatrixParametersSingleBulk(OpportunityMatrixParameters):
    bulk_id: str


class ConnectivityMatrixParameters(BaseModel):
    mode: str
    profile: str
    bulk_id: list[str]
    max_traveltime: int
    s3_folder: Optional[str] = ""


ConnectivityMatrixExample = {
    "mode": "walking",
    "profile": "standard",
    "bulk_id": ["861f8d55fffffff"],
    "max_traveltime": 20,
    "s3_folder": "test",
}


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


examples = {
    "travel_time_matrix": {
        "active_mobility": {
            "summary": "Opportunity Matrix for Active Mobility",
            "value": {
                "bulk_id": ["861f8d55fffffff"],
                "calculation_resolution": 10,
                "isochrone_dto": {
                    "mode": "walking",
                    "settings": {"travel_time": 20, "speed": 5, "walking_profile": "standard"},
                    "starting_point": {
                        "input": [{"lat": 48.1502132, "lon": 11.5696284}],
                    },
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
                    "starting_point": {
                        "input": [{"lat": 48.1502132, "lon": 11.5696284}],
                    },
                    "scenario": {"id": 0, "modus": "default"},
                    "output": {"type": "grid", "resolution": "9"},
                },
                "s3_folder": "test",
            },
        },
    },
    "opportunity_matrix": {
        "active_mobility": {
            "summary": "Opportunity Matrix for Active Mobility",
            "value": {
                "bulk_id": ["861f8d55fffffff"],
                "calculation_resolution": 10,
                "isochrone_dto": {
                    "mode": "walking",
                    "settings": {"travel_time": 20, "speed": 5, "walking_profile": "standard"},
                    "starting_point": {
                        "input": [{"lat": 48.1502132, "lon": 11.5696284}],
                    },
                    "scenario": {"id": 0, "modus": "default"},
                    "output": {"type": "grid", "resolution": 12},
                },
                "scenario_ids": [],
                "user_data_ids": [],
                "compute_base_data": True,
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
                    "starting_point": {
                        "input": [{"lat": 48.1502132, "lon": 11.5696284}],
                    },
                    "scenario": {"id": 0, "modus": "default"},
                    "output": {"type": "grid", "resolution": "9"},
                },
                "scenario_ids": [],
                "user_data_ids": [],
                "compute_base_data": True,
                "s3_folder": "test",
            },
        },
    },
}
