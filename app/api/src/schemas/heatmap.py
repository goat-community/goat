from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, root_validator, validator
from sqlmodel import SQLModel

from src.schemas.isochrone import (
    CalculationTypes,
    IsochroneAccessMode,
    IsochroneCyclingProfile,
    IsochroneScenario,
    IsochroneWalkingProfile,
)


class ComputePoiUser(SQLModel):
    data_upload_id: int


class HeatmapWalkingBulkResolution(int, Enum):
    """H3 Resolution Bulk."""

    resolution = 6


class HeatmapWalkingCalculationResolution(int, Enum):
    """H3 Resolution Calculation."""

    resolution = 10


class HeatmapMode(Enum):
    walking = "walking"
    cycking = "cycling"


class HeatmapType(Enum):
    gravity = "gravity"
    connectivity = "connectivity"
    cumulative = "cumulative"
    closest_average = "closest_average"

class ReturnTypeHeatmap(Enum):
    geojson = "geojson"
    csv = "csv"
    geobuf = "geobuf"
    pbf = "pbf"
    shapefile = "shapefile"


class AnalysisUnit(Enum):
    hexagon = "hexagon"
    square = "square"
    building = "building"
    point = "point"


class HeatmapBaseSpeed(Enum):
    """Speed in km/h"""

    walking = 5.0
    cycling = 15.0


class HeatmapBase(BaseModel):
    max_traveltime: int
    weight: int


class HeatmapConfigGravity(HeatmapBase):
    sensitivity: int

class HeatmapClosestAverage(HeatmapBase):
    max_count: int


class HeatmapSettings(BaseModel):
    """Setting for different heatmap types"""

    mode: HeatmapMode = Field(HeatmapMode.walking, description="Isochrone Mode")
    max_travel_time: int = Field(
        10,
        gt=0,
        description="Travel time in **minutes**",
    )
    walking_profile: Optional[IsochroneWalkingProfile] = Field(
        IsochroneWalkingProfile.STANDARD.value,
        description="Walking profile.",
    )
    cycling_profile: Optional[IsochroneCyclingProfile] = Field(
        IsochroneCyclingProfile.STANDARD.value,
        description="Cycling profile.",
    )
    scenario: Optional[IsochroneScenario] = Field(
        {
            "id": 1,
            "modus": CalculationTypes.default,
        },
        description="Isochrone scenario parameters. Only supported for POIs and Building scenario at the moment",
    )
    analysis_unit: AnalysisUnit = (
        Field(AnalysisUnit.hexagon, description="Analysis unit for the heatmap"),
    )
    analysis_unit_size: Optional[int] = (
        Field(10, description="Size of the analysis unit in meters"),
    )
    heatmap_type: HeatmapType = (
        Field(HeatmapType.gravity, description="Type of heatmap to compute"),
    )
    heatmap_config: dict
    return_type: ReturnTypeHeatmap = Field(
        ReturnTypeHeatmap.geobuf, description="Return type of the heatmap"
    )

    @validator("heatmap_config")
    def heatmap_config_schema(cls, value, values):
        """
        Validate each part of heatmap_config against validator class corresponding to heatmap_type
        """
        validator_classes = {"gravity": HeatmapConfigGravity, "closest_average": HeatmapClosestAverage}

        heatmap_type = values["heatmap_type"].value
        if heatmap_type not in validator_classes.keys():
            raise ValueError(f"Validation for type {heatmap_type} not found.")
        validator_class = validator_classes[heatmap_type]
        heatmap_config = value
        for category in heatmap_config:
            validator_class(**heatmap_config[category])

        return value


"""
Body of the request
"""
request_examples = {
    "compute_poi_user": {"data_upload_id": 1},
    "heatmap_config": """{"supermarket":{"sensitivity":250000,"weight":1}}""",
}
