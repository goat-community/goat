from typing import Dict, List
from pydantic import BaseModel
from geojson_pydantic import Feature, Polygon


class IsochroneBase(BaseModel):
    """Base class for isochrone models"""

    user_id: int
    minutes: int
    speed: int
    n: int
    modus: str
    routing_profile: str


class IsochroneSingle(IsochroneBase):
    """Single Isochrone DTO"""

    x: float
    y: float
    concavity: str
    scenario_id: int


class IsochroneMulti(BaseModel):
    """Multiple Isochrone DTO"""

    alphashape_parameter: str
    region_type: str
    region: List[str]
    scenario_id: int
    amenities: List[str]


class IsochroneExport(BaseModel):
    """Isochrone export DTO"""

    return_type: str
    objectid: int


class IsochroneGeoJSONProperties(BaseModel):
    """Isochrone GeoJSON properties in the response"""

    gid: int
    step: int
    modus: int
    speed: float
    userid: int
    objectid: int
    parent_id: int
    population: List[Dict[str, int]]
    coordinates: List[List[float]]
    scenario_id: int
    routing_profile: str
    alphashape_parameter: float


class IsochroneGeoJSONResponse(Feature[Polygon, IsochroneGeoJSONProperties]):
    """Isochrone GeoJSON feature in the response"""

    pass
