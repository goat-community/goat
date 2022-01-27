from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio.session import AsyncSession

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


@router.post("/single", response_model=Any)
async def calculate_single_isochrone(
    *, db: AsyncSession = Depends(deps.get_db), isochrone_in: IsochroneSingle
) -> Any:
    """
    Calculate single isochrone.
    """

    isochrone = await crud.isochrone.calculate_single_isochrone(db=db, obj_in=isochrone_in)
    return isochrone


@router.post("/multi", response_model=IsochroneMultiCollection)
async def calculate_multi_isochrone(
    *, db: AsyncSession = Depends(deps.get_db), isochrone_in: IsochroneMulti
) -> Any:
    """
    Calculate multi isochrone.
    """

    isochrone = await crud.isochrone.calculate_multi_isochrones(db=db, obj_in=isochrone_in)
    return isochrone


@router.post("/multi/count-pois", response_model=IsochroneMultiCountPoisCollection)
async def count_pois_multi_isochrones(
    *, db: AsyncSession = Depends(deps.get_db), isochrone_in: IsochroneMultiCountPois
) -> Any:
    """
    Count pois under study area.
    """

    feature_collection = await crud.isochrone.count_pois_multi_isochrones(
        db=db, obj_in=isochrone_in
    )
    return feature_collection


@router.post("/export", response_class=StreamingResponse)
async def export_isochrones(
    *, db: AsyncSession = Depends(deps.get_db), isochrone_in: IsochroneExport
) -> Any:
    """
    Export isochrones.
    """
    file_response = await crud.isochrone.export_isochrone(db=db, obj_in=isochrone_in)
    return file_response
