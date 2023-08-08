from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, validator
from sqlmodel import SQLModel

from src.schemas.isochrone import (
    CalculationTypes,
    IsochroneCyclingProfile,
    IsochroneScenario,
    IsochroneWalkingProfile,
)


class ComputePoiUser(SQLModel):
    data_upload_id: int


class HeatmapBulkResolution(int, Enum):
    """H3 Resolution Bulk."""

    active_mobility = 6
    motorized_transport = 6


class HeatmapCalculationResolution(int, Enum):
    """H3 Resolution Calculation."""

    active_mobility = 10
    motorized_transport = 8


class HeatmapMode(Enum):
    walking = "walking"
    cycling = "cycling"
    transit = "transit"


class HeatmapProfile(Enum):
    standard = "standard"


class AggregatingDataSource(Enum):
    population = "population"


class HeatmapType(Enum):
    modified_gaussian = "modified_gaussian"
    combined_cumulative_modified_gaussian = "combined_cumulative_modified_gaussian"
    connectivity = "connectivity"
    cumulative = "cumulative"
    closest_average = "closest_average"
    aggregated_data = "aggregated_data"
    modified_gaussian_population = "modified_gaussian_population"


class ReturnTypeHeatmap(Enum):
    GEOJSON = "geojson"
    CSV = "csv"
    GEOBUF = "geobuf"
    SHAPEFILE = "shapefile"
    GEOPACKAGE = "geopackage"
    KML = "kml"
    XLSX = "xlsx"


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
    visible: bool = False


class HeatmapConfigGravity(HeatmapBase):
    sensitivity: int


class HeatmapConfigCombinedGravity(HeatmapConfigGravity):
    static_traveltime: int


class HeatmapClosestAverage(HeatmapBase):
    max_count: int


class HeatmapConfigConnectivity(BaseModel):
    max_traveltime: int = Field(None, le=60)


class HeatmapConfigAggregatedData(BaseModel):
    source: AggregatingDataSource


class HeatmapSettingsBase(BaseModel):
    study_area_ids: List[int]
    resolution: int = Field(None, ge=6, le=10)
    heatmap_type: HeatmapType
    heatmap_config: dict
    analysis_unit: AnalysisUnit
    analysis_unit_size: Optional[int] = Field(10, description="Size of the analysis")
    return_type: ReturnTypeHeatmap = "geojson"
    scenario: Optional[IsochroneScenario] = Field(
        {
            "id": 1,
            "modus": CalculationTypes.default,
        },
        description="Isochrone scenario parameters. Only supported for POIs and Building scenario at the moment",
    )


class HeatmapSettingsAggregatedData(HeatmapSettingsBase):
    heatmap_config: HeatmapConfigAggregatedData


class HeatmapSettings0(HeatmapSettingsBase):
    """Setting for different heatmap types"""

    mode: HeatmapMode = Field(HeatmapMode.walking.value, description="Isochrone Mode")
    walking_profile: Optional[IsochroneWalkingProfile] = Field(
        IsochroneWalkingProfile.STANDARD.value,
        description="Walking profile.",
    )
    cycling_profile: Optional[IsochroneCyclingProfile] = Field(
        IsochroneCyclingProfile.STANDARD.value,
        description="Cycling profile.",
    )

    heatmap_type: HeatmapType = Field(
        HeatmapType.modified_gaussian, description="Type of heatmap to compute"
    )

    @validator("heatmap_config")
    def heatmap_config_schema_connectivity(cls, value, values):
        if values["heatmap_type"] != HeatmapType.connectivity:
            return value
        else:
            return HeatmapConfigConnectivity(**value)

    @validator("heatmap_config")
    def heatmap_config_schema(cls, value, values):
        """
        Validate each part of heatmap_config against validator class corresponding to heatmap_type
        """
        if values["heatmap_type"] == HeatmapType.connectivity:
            # This validator should not apply to connectivity heatmap
            return value

        validator_classes = {
            "modified_gaussian": HeatmapConfigGravity,
            "combined_cumulative_modified_gaussian": HeatmapConfigCombinedGravity,
            "modified_gaussian_population": HeatmapConfigCombinedGravity,
            "closest_average": HeatmapClosestAverage,
        }

        heatmap_type = values["heatmap_type"].value
        if heatmap_type not in validator_classes.keys():
            raise ValueError(f"Validation for type {heatmap_type} not found.")
        validator_class = validator_classes[heatmap_type]
        heatmap_config = value
        for opportunity in heatmap_config:
            for category in heatmap_config[opportunity]:
                category_settings = heatmap_config[opportunity][category]
                validator_class(**category_settings)

        return value


class HeatmapSettings(BaseModel):
    def __new__(cls, *args, **kwargs):
        heatmap_type = kwargs.get("heatmap_type")
        if (
            heatmap_type == HeatmapType.aggregated_data.value
            or heatmap_type == HeatmapType.aggregated_data
        ):
            return HeatmapSettingsAggregatedData(*args, **kwargs)
        else:
            return HeatmapSettings0(*args, **kwargs)


class BulkTravelTime(BaseModel):
    west: list[int]
    north: list[int]
    zoom: list[int]
    width: list[int]
    height: list[int]
    grid_ids: list[int]
    travel_times: list[list[int]]


"""
Body of the request
"""
request_examples_ = {
    "compute_poi_user": {"data_upload_id": 1},
    "heatmap_configuration": """{"supermarket":{"sensitivity":250000,"weight":1}}""",
}


request_examples = {
    "modified_gaussian_hexagon_10": {
        "summary": "Gravity heatmap with hexagon resolution 10",
        "value": {
            "mode": "walking",
            "study_area_ids": [91620000],
            "walking_profile": "standard",
            "scenario": {
                "id": 1,
                "name": "default",
            },
            "heatmap_type": "modified_gaussian",
            "analysis_unit": "hexagon",
            "resolution": 10,
            "return_type": "geojson",
            "heatmap_config": {
                "poi": {
                    "atm": {"weight": 1, "sensitivity": 250000, "max_traveltime": 20},
                    "bar": {"weight": 1, "sensitivity": 250000, "max_traveltime": 20},
                    "gym": {"weight": 1, "sensitivity": 350000, "max_traveltime": 20},
                },
            },
        },
    },
    "connectivity_heatmap_6_walking": {
        "summary": "Connectivity heatmap with hexagon resolution 6 Walking",
        "value": {
            "mode": "walking",
            "study_area_ids": [91620000],
            "walking_profile": "standard",
            "scenario": {
                "id": 1,
                "name": "default",
            },
            "heatmap_type": "connectivity",
            "analysis_unit": "hexagon",
            "resolution": 6,
            "return_type": "geojson",
            "heatmap_config": {
                "max_traveltime": 20,
            },
        },
    },
    "connectivity_heatmap_6_transit": {
        "summary": "Connectivity heatmap with hexagon resolution 6 Public Transport",
        "value": {
            "mode": "transit",
            "study_area_ids": [91620000],
            "scenario": {
                "id": 1,
                "name": "default",
            },
            "heatmap_type": "connectivity",
            "analysis_unit": "hexagon",
            "resolution": 6,
            "return_type": "geojson",
            "heatmap_config": {
                "max_traveltime": 60,
            },
        },
    },
    "modified_gaussian_hexagon_9": {
        "summary": "Gravity heatmap with hexagon resolution 9",
        "value": {
            "mode": "walking",
            "study_area_ids": [91620000],
            "walking_profile": "standard",
            "scenario": {
                "id": 1,
                "name": "default",
            },
            "heatmap_type": "modified_gaussian",
            "analysis_unit": "hexagon",
            "resolution": 9,
            "return_type": "geojson",
            "heatmap_config": {
                "poi": {
                    "atm": {"weight": 1, "sensitivity": 250000, "max_traveltime": 20},
                    "bar": {"weight": 1, "sensitivity": 250000, "max_traveltime": 20},
                    "gym": {"weight": 1, "sensitivity": 350000, "max_traveltime": 20},
                },
            },
        },
    },
    "modified_gaussian_hexagon_6": {
        "summary": "Gravity heatmap with hexagon resolution 6",
        "value": {
            "mode": "walking",
            "study_area_ids": [91620000],
            "walking_profile": "standard",
            "scenario": {
                "id": 1,
                "name": "default",
            },
            "heatmap_type": "modified_gaussian",
            "analysis_unit": "hexagon",
            "resolution": 6,
            "return_type": "geojson",
            "heatmap_config": {
                "poi": {
                    "atm": {"weight": 1, "sensitivity": 250000, "max_traveltime": 20},
                    "bar": {"weight": 1, "sensitivity": 250000, "max_traveltime": 20},
                    "gym": {"weight": 1, "sensitivity": 350000, "max_traveltime": 20},
                },
            },
        },
    },
    "combined_modified_gaussian_hexagon_6": {
        "summary": "Combined Gravity heatmap with hexagon resolution 6",
        "value": {
            "mode": "walking",
            "study_area_ids": [91620000],
            "walking_profile": "standard",
            "scenario": {
                "id": 1,
                "name": "default",
            },
            "heatmap_type": "combined_cumulative_modified_gaussian",
            "analysis_unit": "hexagon",
            "resolution": 6,
            "return_type": "geojson",
            "heatmap_config": {
                "poi": {
                    "atm": {
                        "weight": 1,
                        "sensitivity": 250000,
                        "max_traveltime": 20,
                        "static_traveltime": 5,
                    },
                    "bar": {
                        "weight": 1,
                        "sensitivity": 250000,
                        "max_traveltime": 20,
                        "static_traveltime": 5,
                    },
                    "gym": {
                        "weight": 1,
                        "sensitivity": 350000,
                        "max_traveltime": 20,
                        "static_traveltime": 5,
                    },
                },
            },
        },
    },
    "closest_average_hexagon_10": {
        "summary": "Closest average heatmap with hexagon resolution 10",
        "value": {
            "mode": "walking",
            "study_area_ids": [91620000],
            "walking_profile": "standard",
            "scenario": {
                "id": 1,
                "name": "default",
            },
            "heatmap_type": "closest_average",
            "analysis_unit": "hexagon",
            "resolution": 10,
            "return_type": "geojson",
            "heatmap_config": {
                "poi": {
                    "atm": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "bar": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "gym": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "pub": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "bank": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "cafe": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "fuel": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "park": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "yoga": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "hotel": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "bakery": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "cinema": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "forest": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "museum": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "butcher": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "dentist": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "nursery": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "bus_stop": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "pharmacy": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "post_box": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "fast_food": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "gymnasium": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "nightclub": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "recycling": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "tram_stop": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "playground": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "realschule": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "restaurant": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "car_sharing": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "convenience": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "grundschule": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "hypermarket": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "marketplace": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "post_office": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "supermarket": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "bike_sharing": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "discount_gym": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "kindergarten": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "rail_station": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "subway_entrance": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "charging_station": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "organic_supermarket": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "discount_supermarket": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "general_practitioner": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "swimming_pool_outdoor": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "hauptschule_mittelschule": {
                        "weight": 1,
                        "max_count": 1,
                        "max_traveltime": 20,
                    },
                },
            },
        },
    },
    "closest_average_hexagon_9": {
        "summary": "Closest average hexagon with resolution 9",
        "value": {
            "mode": "walking",
            "study_area_ids": [91620000],
            "walking_profile": "standard",
            "scenario": {
                "id": 1,
                "name": "default",
            },
            "heatmap_type": "closest_average",
            "analysis_unit": "hexagon",
            "resolution": 9,
            "return_type": "geojson",
            "heatmap_config": {
                "poi": {
                    "atm": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "bar": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "gym": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                },
            },
        },
    },
    "closest_average_hexagon_6": {
        "summary": "Closest average hexagon with resolution 6",
        "value": {
            "mode": "walking",
            "study_area_ids": [91620000],
            "walking_profile": "standard",
            "scenario": {
                "id": 1,
                "name": "default",
            },
            "heatmap_type": "closest_average",
            "analysis_unit": "hexagon",
            "resolution": 6,
            "return_type": "geojson",
            "heatmap_config": {
                "poi": {
                    "atm": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "bar": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                    "gym": {"weight": 1, "max_count": 1, "max_traveltime": 20},
                },
            },
        },
    },
    "connectivity_heatmap_10": {
        "summary": "Connectivity heatmap with hexagon resolution 10",
        "value": {
            "mode": "walking",
            "study_area_ids": [91620000],
            "walking_profile": "standard",
            "scenario": {
                "id": 1,
                "name": "default",
            },
            "heatmap_type": "connectivity",
            "analysis_unit": "hexagon",
            "resolution": 10,
            "return_type": "geojson",
            "heatmap_config": {"max_traveltime": 10},
        },
    },
    "aggregated_data_heatmap_10": {
        "summary": "Aggregated data with hexagon resolution 10",
        "value": {
            "study_area_ids": [91620000],
            "scenario": {
                "id": 1,
                "name": "default",
            },
            "heatmap_type": "aggregated_data",
            "analysis_unit": "hexagon",
            "resolution": 10,
            "heatmap_config": {"source": "population"},
        },
    },
    "modified_gaussian_population_6": {
        "summary": "Modified gaussian population with hexagon resolution 6",
        "value": {
            "mode": "walking",
            "study_area_ids": [91620000],
            "walking_profile": "standard",
            "scenario": {
                "id": 1,
                "name": "default",
            },
            "heatmap_type": "modified_gaussian_population",
            "analysis_unit": "hexagon",
            "resolution": 6,
            "return_type": "geojson",
            "heatmap_config": {
                "poi": {
                    "atm": {
                        "weight": 1,
                        "sensitivity": 250000,
                        "max_traveltime": 20,
                        "static_traveltime": 5,
                    },
                    "bar": {
                        "weight": 1,
                        "sensitivity": 250000,
                        "max_traveltime": 20,
                        "static_traveltime": 5,
                    },
                    "gym": {
                        "weight": 1,
                        "sensitivity": 350000,
                        "max_traveltime": 20,
                        "static_traveltime": 5,
                    },
                },
            },
        },
    },
}

# sort request_examples by resolution
try:
    request_examples = {k: v for k, v in sorted(request_examples.items(), key=lambda item: item[1]['value']['resolution'])}
except Exception:
    pass

# add warning to request_examples with high resolution
for key, value in request_examples.items():
    if value["value"]["resolution"] > 6:
        request_examples[key]["summary"] += " (Warning! May freeze browser.)"