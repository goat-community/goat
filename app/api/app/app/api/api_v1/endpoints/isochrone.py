from typing import Any

from fastapi import APIRouter, Depends
from fastapi.param_functions import Body
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.schemas.isochrone import (
    IsochroneMultiCountPois,
    IsochroneMultiCountPoisCollection,
    IsochroneSingleCollection,
    IsochroneMultiCollection,
    IsochroneMulti,
    IsochroneSingle,
)

router = APIRouter()


@router.post("/single", response_model=IsochroneSingleCollection)
async def calculate_single_isochrone(
    *, db: Session = Depends(deps.get_db), isochrone_in: IsochroneSingle
) -> Any:
    """
    Calculate single isochrone.
    """

    isochrone = crud.isochrone.calculate_single_isochrone(db=db, obj_in=isochrone_in)
    return isochrone


@router.post("/multi", response_model=IsochroneMultiCollection)
async def calculate_multi_isochrone(
    *, db: Session = Depends(deps.get_db), isochrone_in: IsochroneMulti
) -> Any:
    """
    Calculate multi isochrone.
    """

    isochrone = crud.isochrone.calculate_multi_isochrones(db=db, obj_in=isochrone_in)
    return isochrone


@router.post("/multi/count-pois", response_model=IsochroneMultiCountPoisCollection)
async def count_pois_multi_isochrones(
    *,
    db: Session = Depends(deps.get_db),
    isochrone_in: IsochroneMultiCountPois = Body(
        ...,
        examples={
            "study_area": {
                "summary": "Count pois on study area",
                "value": {
                    "region_type": "study_area",
                    "region": "POINT(7.8383676846236225 48.02455137958364)",
                    "user_id": 120,
                    "scenario_id": "0",
                    "modus": "default",
                    "minutes": 10,
                    "speed": 5,
                    "amenities": [
                        "nursery",
                        "kindergarten",
                        "grundschule",
                        "realschule",
                        "werkrealschule",
                        "gymnasium",
                        "library",
                    ],
                },
            },
            "draw": {
                "summary": "Count pois on drawn area",
                "value": {
                    "region_type": "draw",
                    "region": "POLYGON((7.8326089040193585 47.993884998730266,7.837941031304315 47.996363977305464,7.844115073423737 47.99497426156083,7.842880264999852 47.9918190922715,7.837323627092372 47.99088001653931,7.8326089040193585 47.993884998730266))",
                    "user_id": 122,
                    "scenario_id": "0",
                    "modus": "default",
                    "minutes": 10,
                    "speed": 5,
                    "amenities": [
                        "nursery",
                        "kindergarten",
                        "grundschule",
                        "realschule",
                        "werkrealschule",
                        "gymnasium",
                        "library",
                    ],
                },
            },
        },
    )
) -> Any:
    """
    Count pois under study area.
    """

    feature_collection = crud.isochrone.count_pois_multi_isochrones(
        db=db, obj_in=isochrone_in
    )
    return feature_collection
