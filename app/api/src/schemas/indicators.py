from multiprocessing.sharedctypes import Value
from typing import Any, Optional, List
from pydantic import BaseModel, Field, root_validator, validator
from src.resources.enums import ReturnType
from typing import Union

station_config_example = {
    "groups": {
        "0": "B",  # route_type: category of public transport route
        "1": "A",
        "2": "A",
        "3": "C",
        "4": "B",
        "5": "B",
        "6": "B",
        "7": "B",
        "11": "B",
        "12": "B",
    },
    "time_frequency": [0, 4, 10, 19, 39, 60, 119],
    "categories": [
        {
            "A": 1,  # i.e. types of transports in category A are in transport stop category I
            "B": 1,
            "C": 2,
        },
        {"A": 1, "B": 2, "C": 3},
        {"A": 2, "B": 3, "C": 4},
        {"A": 3, "B": 4, "C": 5},
        {"A": 4, "B": 5, "C": 6},
        {"A": 5, "B": 6, "C": 6},
    ],
    "classification": {
        "1": {300: "A", 500: "A", 750: "B", 1000: "C"},
        "2": {300: "A", 500: "B", 750: "C", 1000: "D"},
        "3": {300: "B", 500: "C", 750: "D", 1000: "E"},
        "4": {300: "C", 500: "D", 750: "E", 1000: "F"},
        "5": {300: "D", 500: "E", 750: "F"},
        "6": {300: "E", 500: "F"},
        "7": {300: "F"},
    },
}


class CalculateOevGueteklassenParameters(BaseModel):
    start_time: int = 25200
    end_time: int = 32400
    weekday: int = 1
    study_area_ids: Optional[List[int]]
    return_type: ReturnType = ReturnType.geojson
    station_config: dict

    @validator("start_time", "end_time")
    def seconds_validator(cls, v):
        if v < 0 or v > 86400:
            raise ValueError("Should be between or equal to 0 and 86400")
        return v

    @validator("weekday")
    def weekday_validator(cls, v):
        if v < 1 or v > 7:
            raise ValueError("weekday should be between or equal to 1 and 7")
        return v


oev_gueteklasse_config_example = {
    "start_time": 25200,
    "end_time": 32400,
    "weekday": 1,
    "return_type": ReturnType.geojson,
    "station_config": station_config_example,
    "study_area_ids": [9161, 9184], 
}

#########

local_accessibility_aggregated_indicator_config_example = { 
    "education": {
        '{"nursery": {"sensitivity": 200000, "weight": 1}}',
        '{"kindergarten": {"sensitivity": 300000, "weight": 1}}',
        '{"grundschule": {"sensitivity": 300000, "weight": 1}}',
        '{"hauptschule": {"sensitivity": 300000, "weight": 1}}',
        '{"realschule": {"sensitivity": 300000, "weight": 1}}',
        '{"gymnasium": {"sensitivity": 300000, "weight": 1}}',
    },
    "leisure": {
        '{"restaurant": {"sensitivity": 300000, "weight": 1}}',
        '{"fast_food": {"sensitivity": 300000, "weight": 1}}',
        '{"bar": {"sensitivity": 300000, "weight": 1}}',
        '{"pub": {"sensitivity": 300000, "weight": 1}}',
        '{"cafe": {"sensitivity": 300000, "weight": 1}}',
        '{"nightclub": {"sensitivity": 300000, "weight": 1}}',
        '{"cinema": {"sensitivity": 300000, "weight": 1}}',
        '{"playground": {"sensitivity": 300000, "weight": 1}}',
        '{"park": {"sensitivity": 300000, "weight": 1}}',
        '{"forest": {"sensitivity": 300000, "weight": 1}}',
        '{"gym": {"sensitivity": 300000, "weight": 1}}',
        '{"discount_gym": {"sensitivity": 300000, "weight": 1}}',
    },
    "public_transport": {
        '{"bus_stop": {"sensitivity": 300000, "weight": 1}}',
        '{"tram_stop": {"sensitivity": 300000, "weight": 1}}',
        '{"subway_entrance": {"sensitivity": 300000, "weight": 1}}',
        '{"rail_station": {"sensitivity": 300000, "weight": 1}}',
        '{"bike_sharing": {"sensitivity": 300000, "weight": 1}}',
        '{"car_sharing": {"sensitivity": 300000, "weight": 1}}',
        '{"carsharing": {"sensitivity": 300000, "weight": 1}}',
    },
    "health": {
        '{"dentist": {"sensitivity": 300000, "weight": 1}}',
        '{"general_practitioner": {"sensitivity": 300000, "weight": 1}}',
        '{"pharmacy": {"sensitivity": 300000, "weight": 1}}',
    },
    "living": {
        '{"inhabitant": {"sensitivity": 300000, "weight": 1}}',
        '{"post_office": {"sensitivity": 300000, "weight": 1}}',
        '{"post_box": {"sensitivity": 300000, "weight": 1}}',
        '{"recycling": {"sensitivity": 300000, "weight": 1}}',
    },
    "shop": {
        '{"supermarket": {"sensitivity": 300000, "weight": 1}}',
        '{"discount_supermarket": {"sensitivity": 300000, "weight": 1}}',
        '{"hypermarket": {"sensitivity": 300000, "weight": 1}}',
        '{"marketplace": {"sensitivity": 300000, "weight": 1}}',
        '{"bakery": {"sensitivity": 300000, "weight": 1}}',
        '{"butcher": {"sensitivity": 300000, "weight": 1}}',
    }
}

class CalculateLocalAccessibilityAggregated(BaseModel):
    study_area_id: Optional[int]
    local_accessibility_aggregated_indicator_config: dict
    return_type: ReturnType = ReturnType.geojson # geobuf and geojson needed? (return_type: ReturnType = Union[ReturnType.geojson, ReturnType.geobuf])
    
    # @validator

local_accessibility_aggregated_calculation_config_example = {
    "study_area_id": 9161,
    "local_accessibility_aggregated_indicator_config": local_accessibility_aggregated_indicator_config_example,
    "return_type": ReturnType.geojson
    
}

