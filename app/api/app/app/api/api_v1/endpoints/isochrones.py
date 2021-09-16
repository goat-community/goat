from typing import Any

from fastapi import APIRouter, Depends
from fastapi.param_functions import Body
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.schemas.isochrone import (
    IsochroneExport,
    IsochroneMulti,
    IsochroneMultiCollection,
    IsochroneMultiCountPois,
    IsochroneMultiCountPoisCollection,
    IsochroneSingle,
    IsochroneSingleCollection,
)

router = APIRouter()


@router.post("/single", response_model=IsochroneSingleCollection)
def calculate_single_isochrone(
    *, db: Session = Depends(deps.get_db), isochrone_in: IsochroneSingle
) -> Any:
    """
    Calculate single isochrone.
    """

    isochrone = crud.isochrone.calculate_single_isochrone(db=db, obj_in=isochrone_in)
    return isochrone


@router.post("/multi", response_model=IsochroneMultiCollection)
def calculate_multi_isochrone(
    *, db: Session = Depends(deps.get_db), isochrone_in: IsochroneMulti
) -> Any:
    """
    Calculate multi isochrone.
    """

    isochrone = crud.isochrone.calculate_multi_isochrones(db=db, obj_in=isochrone_in)
    return isochrone


@router.post("/multi/count-pois", response_model=IsochroneMultiCountPoisCollection)
def count_pois_multi_isochrones(
    *, db: Session = Depends(deps.get_db), isochrone_in: IsochroneMultiCountPois
) -> Any:
    """
    Count pois under study area.
    """

    feature_collection = crud.isochrone.count_pois_multi_isochrones(db=db, obj_in=isochrone_in)
    return feature_collection


@router.post("/export", response_class=StreamingResponse)
def export_isochrones(*, db: Session = Depends(deps.get_db), isochrone_in: IsochroneExport) -> Any:
    """
    Export isochrones.
    """
    file_response = crud.isochrone.export_isochrone(db=db, obj_in=isochrone_in)
    return file_response
