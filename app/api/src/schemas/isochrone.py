from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Field, root_validator

"""
Body of the request
"""


class IsochroneTypeEnum(str, Enum):
    single = "single_isochrone"
    multi = "multi_isochrone"
    heatmap = "heatmap"


class IsochroneMultiCountPois(BaseModel):
    user_id: Optional[int]
    scenario_id: Optional[int] = 0
    amenities: List[str]
    minutes: int
    modus: str
    region: List[str]
    region_type: str
    speed: int
    active_upload_ids: Optional[List[int]] = [0]


class CalculationTypes(str, Enum):
    """Calculation types for isochrone."""

    default = "default"
    scenario = "scenario"
    comparison = "comparison"


class IsochroneMode(Enum):
    WALKING = "walking"
    CYCLING = "cycling"
    TRANSIT = "transit"
    CAR = "car"
    BUFFER = "buffer"


class IsochroneWalkingProfile(Enum):
    STANDARD = "standard"


class IsochroneCyclingProfile(Enum):
    STANDARD = "standard"
    PEDELEC = "pedelec"


class IsochroneAccessMode(Enum):
    WALK = "walk"
    BICYCLE = "bicycle"
    CAR = "car"
    # CAR_PARK = "car_park" //TODO: not supported yet


class IsochroneTransitMode(Enum):
    BUS = "bus"
    TRAM = "tram"
    RAIL = "rail"
    SUBWAY = "subway"
    FERRY = "ferry"
    CABLE_CAR = "cable_car"
    GONDOLA = "gondola"
    FUNICULAR = "funicular"


class IsochroneEgressMode(Enum):
    WALK = "walk"
    # BICYCLE = "bicycle" //TODO: not supported yet


class IsochroneOutputType(Enum):
    GRID = "grid"
    GEOJSON = "geojson"
    NETWORK = "network"

    CSV = "csv"
    GEOBUF = "geobuf"
    SHAPEFILE = "shapefile"
    GEOPACKAGE = "geopackage"
    KML = "kml"
    XLSX = "xlsx"


class IsochroneDecayFunctionType(Enum):
    LOGISTIC = "logistic"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    STEP = "step"


class IsochroneMultiRegionType(Enum):
    STUDY_AREA = "study_area"
    DRAW = "draw"


class IsochroneDecayFunction(BaseModel):
    type: Optional[str] = Field(
        IsochroneDecayFunctionType.LOGISTIC, description="Decay function type"
    )
    standard_deviation_minutes: Optional[int] = Field(
        12, description="Standard deviation in minutes"
    )
    width_minutes: Optional[int] = Field(10, description="Width in minutes")


class IsochroneSettings(BaseModel):
    # === SETTINGS FOR WALKING AND CYCLING ===#
    travel_time: Optional[int] = Field(
        10,
        gt=0,
        description="Travel time in **minutes**",
    )
    buffer_distance: Optional[int] = Field(
        1000,
        gt=50,
        le=3000,
        description="Buffer distance in **meters**",
    )
    speed: Optional[float] = Field(
        5,
        gt=0,
        le=25,
        description="Walking or Cycling speed in **km/h** **(Not considered for PT or CAR)**",
    )
    walking_profile: Optional[IsochroneWalkingProfile] = Field(
        IsochroneWalkingProfile.STANDARD.value,
        description="Walking profile. **(Not considered for PT)**",
    )
    cycling_profile: Optional[IsochroneCyclingProfile] = Field(
        IsochroneCyclingProfile.STANDARD.value,
        description="Cycling profile. **(Not considered for PT)**",
    )
    # === SETTINGS FOR CAR AND PT ===#
    weekday: Optional[int] = Field(
        0, ge=0, le=6, description="(PT) Departure weekday, 0=Monday, 6=Sunday"
    )
    from_time: Optional[int] = Field(
        25200, gt=0, lt=86400, description="(PT) From time. Number of seconds since midnight"
    )
    to_time: Optional[int] = Field(
        39600, gt=0, lt=86400, description="(PT) To time . Number of seconds since midnight"
    )
    transit_modes: List[IsochroneTransitMode] = Field(
        [
            IsochroneTransitMode.BUS.value,
            IsochroneTransitMode.TRAM.value,
            IsochroneTransitMode.SUBWAY.value,
            IsochroneTransitMode.RAIL.value,
        ],
        description="Public Transport modes",
        unique_items=True,
    )
    access_mode: Optional[IsochroneAccessMode] = Field(
        IsochroneAccessMode.WALK, description="(PT) Access mode"
    )
    egress_mode: Optional[IsochroneEgressMode] = Field(
        IsochroneEgressMode.WALK, description="(PT) Egress mode"
    )
    bike_speed: Optional[float] = Field(15, gt=0, le=15, description="(PT) Bike speed")
    walk_speed: Optional[float] = Field(5, gt=0, le=15, description="(PT) Walk speed")
    bike_traffic_stress: Optional[int] = Field(
        4, ge=1, le=4, description="(PT) Bike traffic stress. 1: Low stress, 4: Very high stress"
    )
    max_rides: Optional[int] = Field(4, description="(PT) Max number of rides")
    max_bike_time: Optional[int] = Field(
        20,
        description="(PT) Max bike time (in minutes) to access and egress the transit network, or to make transfers within the network.",
    )
    max_walk_time: Optional[int] = Field(
        20,
        description="(PT) The maximum walking time (in minutes) to access and egress the transit network, or to make transfers within the network. Defaults to no restrictions, as long as max_trip_duration is respected. The max time is considered separately for each leg (e.g. if you set max_walk_time to 20, you could potentially walk up to 20 minutes to reach transit, and up to another 20 minutes to reach the destination after leaving transit).",
    )
    percentiles: Optional[List[int]] = Field(
        [5, 25, 50, 75, 95],
        description="(PT) Specifies the percentile to use when returning accessibility estimates within the given time window. Please note that this parameter is applied to the travel time estimates that generate the accessibility results, and not to the accessibility distribution itself (i.e. if the 25th percentile is specified, the accessibility is calculated from the 25th percentile travel time, which may or may not be equal to the 25th percentile of the accessibility distribution itself). Defaults to 50, returning the accessibility calculated from the median travel time. If a vector with length bigger than 1 is passed, the output contains an additional column that specifies the percentile of each accessibility estimate. Due to upstream restrictions, only 5 percentiles can be specified at a time. For more details, please see R5 documentation at https://docs.conveyal.com/analysis/methodology#accounting-for-variability.",
    )
    monte_carlo_draws: Optional[int] = Field(
        200,
        gt=0,
        le=200,
        description="(PT) The number of Monte Carlo draws to perform per time window minute when calculating travel time matrices and when estimating accessibility.",
    )
    decay_function: Optional[IsochroneDecayFunction] = Field(
        {
            "type": "logistic",
            "standard_deviation_minutes": 12,
            "width_minutes": 10,
        },
        description="(PT) A family of monotonically decreasing functions from travel times to weight factors in the range [0...1]. This determines how much an opportunity at a given travel time is weighted when included in an accessibility value",
    )


class IsochroneScenario(BaseModel):
    id: Optional[int] = Field(..., description="Scenario ID")
    modus: Optional[CalculationTypes] = Field(
        CalculationTypes.default, description="Scenario modus"
    )


class IsochroneStartingPointCoord(BaseModel):
    lat: float = Field(..., gt=-90, lt=90)
    lon: float = Field(..., gt=-180, lt=180)


class IsochroneStartingPoint(BaseModel):
    region_type: Optional[IsochroneMultiRegionType] = Field(
        IsochroneMultiRegionType.STUDY_AREA,
        description="The type of region to use for the multi-isochrone calculation",
    )
    region: Optional[List[str]] = Field(
        [],
        description="The region to use for the multi-isochrone calculation. If region_type is study_area, this is a list of study area IDs. If region_type is draw, this is a list of WKT polygons.",
    )
    input: Union[List[str], List[IsochroneStartingPointCoord]] = Field(
        ...,
        description="The input to use for the multi-isochrone calculation. It can be a list of amenities, or a list of coordinates.",
    )


class IsochroneOutput(BaseModel):
    type: Optional[IsochroneOutputType] = Field(
        IsochroneOutputType.GRID,
        description="The type of response isochrone is generated. If type is `grid`, the output is a grid of accessibility values on every cell. If type is `geojson`, the output is a geojson file with the accessibility distribution for every step.",
    )
    steps: Optional[int] = Field(2, description="Number of isochrone steps for 'geojson' output")
    resolution: Optional[int] = Field(
        9,
        description="GRID Resolution for `grid` output type. Default (9 for PT Isochrone, 10 for Waking and Cycling Isochrone",
    )


class IsochroneDTO(BaseModel):
    mode: IsochroneMode = Field(IsochroneAccessMode.WALK, description="Isochrone Mode")
    settings: IsochroneSettings = Field(..., description="Isochrone settings parameters")
    scenario: Optional[IsochroneScenario] = Field(
        {
            "id": 1,
            "modus": CalculationTypes.default,
        },
        description="Isochrone scenario parameters. Only supported for Walking and Cycling Isochrones",
    )
    starting_point: Optional[IsochroneStartingPoint] = Field(
        ...,
        description="Isochrone starting points. If multiple starting points are specified, the isochrone is considered a multi-isochrone calculation. **Multi-Isochrone Only works for Walking and Cycling Isochrones**. Alternatively, amenities can be used to specify the starting points for multi-isochrones.",
    )
    output: Optional[IsochroneOutput] = Field(..., description="Isochrone output parameters")

    class Config:
        extra = "forbid"

    @root_validator
    def validate_output(cls, values):
        """Validate"""

        if not values.get("mode"):
            raise ValueError("Isochrone mode is required")

        if not values.get("starting_point"):
            raise ValueError("Isochrone starting point is required")

        # Validation check on grid resolution and number of steps for geojson for walking and cycling isochrones
        if (
            values["output"].type.value == IsochroneOutputType.GRID.value
            and values["output"].resolution not in [9, 10, 11, 12]
            and values["mode"].value
            in [
                IsochroneAccessMode.WALK.value,
                IsochroneAccessMode.BICYCLE.value,
            ]
        ):
            raise ValueError(
                "Resolution must be between 9 and 14 for walking and cycling isochrones"
            )

        # validate to check if buffer_distance is provided for "BUFFER" mode
        if (
            values["mode"].value == IsochroneMode.BUFFER.value
            and not values["settings"].buffer_distance
        ):
            raise ValueError("Buffer distance is required for buffer catchment area")

        # Validation check on grid resolution and number of steps for geojson for public transport isochrones
        if (
            values["output"].type.value == IsochroneOutputType.GRID.value
            and values["output"].resolution not in [9, 10]
            and values["mode"].value
            in [
                IsochroneMode.TRANSIT.value,
                IsochroneMode.CAR.value,
            ]
        ):
            raise ValueError("Resolution must be between 9 or 10 for public transport isochrones")

        # Validation for geojso output type
        if values["output"].type.value == IsochroneOutputType.GEOJSON.value and (
            values["output"].steps > 6 or values["output"].steps < 1
        ):
            raise ValueError("Step must be between 1 and 6")

        # Don't allow multi-isochrone calculation for PT and Car Isochrone
        if (
            values["starting_point"]
            and len(values["starting_point"].input) > 1
            and values["mode"].value
            in [
                IsochroneMode.TRANSIT.value,
                IsochroneMode.CAR.value,
            ]
        ):
            raise ValueError("Multi-Isochrone is not supported for Transit and Car")

        # For walking and cycling travel time maximumn should be 20 minutes and speed to m/s
        if values["mode"].value in [IsochroneMode.WALKING.value, IsochroneMode.CYCLING.value]:
            if values["settings"].travel_time > 25:
                raise ValueError(
                    "Travel time maximum for walking and cycling should be less or equal to 25 minutes"
                )
            # if values["settings"].speed:
            #     values["settings"].speed = values["settings"].speed / 3.6

        # For PT and Car Isochrone starting point should be only lat lon coordinates and not amenities, travel time smaller than 120 minutes
        if values["mode"].value in [
            IsochroneMode.TRANSIT.value,
            IsochroneMode.CAR.value,
        ]:
            if values["output"].type.value in [
                IsochroneOutputType.GEOJSON.value,
                IsochroneOutputType.NETWORK.value,
            ]:
                raise ValueError("Geojson output is not supported for PT and Car")
            # travel time should be smaller than 120 minutes
            if values["settings"].travel_time > 120:
                raise ValueError("Travel time should be smaller than 120 minutes")

            if len(values["starting_point"].input) > 0:
                for point in values["starting_point"].input:
                    if not isinstance(point, IsochroneStartingPointCoord):
                        raise ValueError("Starting point should be lat lon coordinates")

            # from_time should be smaller than to_time
            if values["settings"].from_time > values["settings"].to_time:
                raise ValueError("Start time should be smaller than end time")

            # # convert bike speed to m/s
            # values["settings"].bike_speed = values["settings"].bike_speed / 3.6
            # # convert walk speed to m/s
            # values["settings"].walk_speed = values["settings"].walk_speed / 3.6

        # If starting-point input length is more than 1 then it should be multi-isochrone and region should be specified
        if len(values["starting_point"].input) > 1 and len(values["starting_point"].region) == 0:
            raise ValueError("Region is not specified for multi-isochrone")

        return values

    @property
    def is_multi(self):
        """Check if multi-isochrone"""
        starting_point_type_is_coord = isinstance(
            self.starting_point.input[0], IsochroneStartingPointCoord
        )

        if len(self.starting_point.input) > 1 and starting_point_type_is_coord:
            return False
        else:
            return True

    @property
    def is_single(self):
        """Check if single-isochrone"""
        return not self.is_multi


# R5
R5AvailableDates = {
    0: "2022-05-16",
    1: "2022-05-17",
    2: "2022-05-18",
    3: "2022-05-19",
    4: "2022-05-20",
    5: "2022-05-21",
    6: "2022-05-22",
}

R5ProjectID = "630c0014aad8682ef8461b44"
R5ProjectIDCarOnly = "64ad9dcf92f18428b858eb2e"

R5TravelTimePayloadTemplate = {
    "accessModes": "WALK",
    "transitModes": "BUS,TRAM,SUBWAY,RAIL",
    "bikeSpeed": 4.166666666666667,
    "walkSpeed": 1.39,
    "bikeTrafficStress": 4,
    "date": "2022-05-16",
    "fromTime": 25200,  # 7 AM
    "toTime": 39600,  # 9 AM
    "maxTripDurationMinutes": 120,
    "decayFunction": {
        "type": "logistic",
        "standard_deviation_minutes": 12,
        "width_minutes": 10,
    },
    "destinationPointSetIds": [],
    "bounds": {
        "north": 48.27059464660387,
        "south": 48.03915718648435,
        "east": 11.327192290815145,
        "west": 11.756388821971976,
    },
    "directModes": "WALK",
    "egressModes": "WALK",
    "fromLat": 48.1502132,
    "fromLon": 11.5696284,
    "zoom": 9,
    "maxBikeTime": 20,
    "maxRides": 4,
    "maxWalkTime": 20,
    "monteCarloDraws": 200,
    "percentiles": [5, 25, 50, 75, 95],
    "variantIndex": -1,
    "workerVersion": "v6.4",
    "projectId": "630c0014aad8682ef8461b44",
}


request_examples = {
    "isochrone": {
        "single_walking_default": {
            "summary": "Single Walking Isochrone with Default Profile",
            "value": {
                "mode": "walking",
                "settings": {
                    "travel_time": "10",
                    "speed": "5",
                    "walking_profile": "standard",
                },
                "starting_point": {
                    "input": [{"lat": 48.1502132, "lon": 11.5696284}],
                },
                "scenario": {"id": 0, "modus": "default"},
                "output": {
                    "type": "grid",
                    "resolution": "12",
                },
            },
        },
        "single_cycling_default": {
            "summary": "Single Cycling Isochrone with Default Profile",
            "value": {
                "mode": "cycling",
                "settings": {
                    "travel_time": "15",
                    "speed": "10",
                    "cycling_profile": "standard",
                },
                "starting_point": {
                    "input": [{"lat": 48.1502132, "lon": 11.5696284}],
                },
                "scenario": {"id": 0, "modus": "default"},
                "output": {
                    "type": "grid",
                    "resolution": "12",
                },
            },
        },
        "pois_multi_isochrone": {
            "summary": "Multi Isochrone with Pois",
            "value": {
                "mode": "walking",
                "settings": {
                    "travel_time": "20",
                    "speed": "5",
                    "walking_profile": "standard",
                },
                "starting_point": {
                    "input": ["nursery"],
                    "region_type": "study_area",
                    "region": [27, 144],
                },
                "scenario": {"id": 0, "modus": "default"},
                "output": {
                    "type": "grid",
                    "resolution": "11",
                },
            },
        },
        "transit_single": {
            "summary": "Single Transit Isochrone",
            "value": {
                "mode": "transit",
                "settings": {
                    "travel_time": "60",
                    "transit_modes": ["bus", "tram", "subway", "rail"],
                    "weekday": "0",  # 0 - Monday, 6 - Sunday
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
                "output": {
                    "type": "grid",
                    "resolution": "9",
                },
            },
        },
        "single_buffer_catchment": {
            "summary": "Single Buffer Catchment",
            "value": {
                "mode": "buffer",
                "settings": {"buffer_distance": "2000"},
                "starting_point": {
                    "input": [{"lat": 48.1502132, "lon": 11.5696284}],
                },
                "scenario": {"id": 0, "modus": "default"},
                "output": {
                    "type": "grid",
                    "resolution": "12",
                },
            },
        },
    },
    "to_export": {
        "single_isochrone": {
            "summary": "Single isochrone",
            "value": {
                "type": "FeatureCollection",
                "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
                "features": [
                    {
                        "type": "Feature",
                        "properties": {
                            "id": 1,
                            "isochrone_calculation_id": 10,
                            "traveltime": 5,
                            "modus": "default",
                            "routing_profile": "walking_standard",
                            "reached_opportunities": {
                                "cafe": 1,
                                "park": {"cnt": 2, "area": 38613},
                                "hotel": 4,
                                "nursery": 1,
                                "sum_pop": 2705,
                                "post_box": 1,
                                "fast_food": 1,
                                "recycling": 1,
                                "tram_stop": 2,
                                "playground": 6,
                                "restaurant": 3,
                                "grundschule": 1,
                                "bike_sharing": 2,
                                "kindergarten": 4,
                                "charging_station": 1,
                                "discount_supermarket": 1,
                            },
                        },
                        "geometry": {
                            "type": "MultiPolygon",
                            "coordinates": [
                                [
                                    [
                                        [11.536658755874345, 48.144345996653797],
                                        [11.537061254841161, 48.143442507346805],
                                        [11.537139521158997, 48.143376435250516],
                                        [11.537191279470155, 48.143343866212035],
                                        [11.5374341, 48.143330799999987],
                                        [11.538859290552271, 48.142221920365188],
                                        [11.544110890465541, 48.142956875316386],
                                        [11.544196172720932, 48.142909469682657],
                                        [11.5444121, 48.1429149],
                                        [11.5446788, 48.142898],
                                        [11.5447, 48.142899],
                                        [11.5447858, 48.1428654],
                                        [11.5449574, 48.1428715],
                                        [11.545375583217202, 48.142822278856279],
                                        [11.545488790304747, 48.14283469276856],
                                        [11.546166696757849, 48.143118735730042],
                                        [11.546642751647143, 48.143376165954912],
                                        [11.546642751647148, 48.143376165954912],
                                        [11.547064889748599, 48.14377999679396],
                                        [11.547015147649532, 48.143872500250502],
                                        [11.546903388987284, 48.143993188934154],
                                        [11.546833928779018, 48.144068918145287],
                                        [11.5461186984767, 48.14500790348432],
                                        [11.545899333743268, 48.145279629977736],
                                        [11.545549163530334, 48.145155553656451],
                                        [11.545461334376407, 48.145125205811034],
                                        [11.543688217515243, 48.146641336661574],
                                        [11.5436489, 48.146629099999977],
                                        [11.54286095056653, 48.146706414261239],
                                        [11.541162533849324, 48.14658405830393],
                                        [11.541035374915147, 48.146570975389658],
                                        [11.540111510317022, 48.146470587868492],
                                        [11.540006178611856, 48.146453661269526],
                                        [11.538424018197535, 48.145817122216336],
                                        [11.538331825367305, 48.145765846095159],
                                        [11.537397113751769, 48.14534096711494],
                                        [11.536658755874345, 48.144345996653797],
                                    ]
                                ]
                            ],
                        },
                    }
                ],
            },
        },
        "multi_isochrones": {
            "summary": "Multi isochrones",
            "value": {
                "type": "FeatureCollection",
                "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
                "features": [
                    {
                        "type": "Feature",
                        "properties": {
                            "id": 1,
                            "isochrone_calculation_id": 10,
                            "traveltime": 5,
                            "modus": "default",
                            "routing_profile": "walking_standard",
                            "reached_opportunities": {
                                "population": {
                                    "study_area1": 1000,
                                    "study_area2": 2000,
                                }
                            },
                        },
                        "geometry": {
                            "type": "MultiPolygon",
                            "coordinates": [
                                [
                                    [
                                        [11.536658755874345, 48.144345996653797],
                                        [11.537061254841161, 48.143442507346805],
                                        [11.537139521158997, 48.143376435250516],
                                        [11.537191279470155, 48.143343866212035],
                                        [11.5374341, 48.143330799999987],
                                        [11.538859290552271, 48.142221920365188],
                                        [11.544110890465541, 48.142956875316386],
                                        [11.544196172720932, 48.142909469682657],
                                        [11.5444121, 48.1429149],
                                        [11.5446788, 48.142898],
                                        [11.5447, 48.142899],
                                        [11.5447858, 48.1428654],
                                        [11.5449574, 48.1428715],
                                        [11.545375583217202, 48.142822278856279],
                                        [11.545488790304747, 48.14283469276856],
                                        [11.546166696757849, 48.143118735730042],
                                        [11.546642751647143, 48.143376165954912],
                                        [11.546642751647148, 48.143376165954912],
                                        [11.547064889748599, 48.14377999679396],
                                        [11.547015147649532, 48.143872500250502],
                                        [11.546903388987284, 48.143993188934154],
                                        [11.546833928779018, 48.144068918145287],
                                        [11.5461186984767, 48.14500790348432],
                                        [11.545899333743268, 48.145279629977736],
                                        [11.545549163530334, 48.145155553656451],
                                        [11.545461334376407, 48.145125205811034],
                                        [11.543688217515243, 48.146641336661574],
                                        [11.5436489, 48.146629099999977],
                                        [11.54286095056653, 48.146706414261239],
                                        [11.541162533849324, 48.14658405830393],
                                        [11.541035374915147, 48.146570975389658],
                                        [11.540111510317022, 48.146470587868492],
                                        [11.540006178611856, 48.146453661269526],
                                        [11.538424018197535, 48.145817122216336],
                                        [11.538331825367305, 48.145765846095159],
                                        [11.537397113751769, 48.14534096711494],
                                        [11.536658755874345, 48.144345996653797],
                                    ]
                                ]
                            ],
                        },
                    }
                ],
            },
        },
    },
    "pois_multi_isochrone_count_pois": {
        "draw": {
            "summary": "Count pois with draw",
            "value": {
                "region_type": "draw",
                "region": [
                    "POLYGON((11.53605224646383 48.15855242757948,11.546141990292947 48.16035646918763,11.54836104048217 48.15434275044706,11.535497483916524 48.15080357881183,11.526586610500429 48.15300113241156,11.531302092152526 48.15799732509075,11.53605224646383 48.15855242757948))"
                ],
                "scenario_id": 0,
                "modus": "default",
                "routing_profile": "walking_standard",
                "minutes": 10,
                "speed": 5,
                "amenities": [
                    "kindergarten",
                    "grundschule",
                    "hauptschule_mittelschule",
                    "realschule",
                    "gymnasium",
                    "library",
                ],
            },
        },
        "study_area": {
            "summary": "Count pois with study area",
            "value": {
                "region_type": "study_area",
                "region": ["1", "2"],
                "scenario_id": 0,
                "modus": "default",
                "routing_profile": "walking_standard",
                "minutes": 10,
                "speed": 5,
                "amenities": [
                    "kindergarten",
                    "grundschule",
                    "hauptschule_mittelschule",
                    "realschule",
                    "gymnasium",
                    "library",
                ],
            },
        },
    },
}
