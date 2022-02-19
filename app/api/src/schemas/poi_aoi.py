from enum import Enum, IntEnum
from typing import Dict, List, Optional, Union

from geojson_pydantic.features import Feature, FeatureCollection
from geojson_pydantic.geometries import MultiPolygon, Polygon
from pydantic import BaseModel, root_validator

"""
Body of the request
"""

class POIAOIBase(BaseModel):
    scenario_id: Optional[int] = 0
    amenities: List[str]
    modus: str
    active_upload_ids: Optional[List[int]] = [0]
    active_study_area_id: Optional[int]

class POIAOIVisualization(POIAOIBase):
    pass

request_examples = {
    "poi_aoi_visualization": {
        "modus": "default",
        "amenities": ["supermarket","discount_supermarket", "kindergarten"],
        "active_upload_ids": [0],
        "scenario_id": 0
    }
}



#hidden_props_client = ["id", "wheelchair", "opening_hours"]
