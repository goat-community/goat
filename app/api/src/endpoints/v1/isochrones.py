from typing import Any

from fastapi import APIRouter, Body, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio.session import AsyncSession

from src import crud
from src.db import models
from src.endpoints import deps
from src.schemas.isochrone import (
    IsochroneExport,
    IsochroneMulti,
    IsochroneMultiCollection,
    IsochroneMultiCountPois,
    IsochroneMultiCountPoisCollection,
    IsochroneSingle,
    IsochroneSingleCollection,
    request_examples,
)

router = APIRouter()


@router.post("/single", response_model=Any)
async def calculate_single_isochrone(
    *,
    db: AsyncSession = Depends(deps.get_db),
    isochrone_in: IsochroneSingle = Body(..., example=request_examples["single"]),
) -> Any:
    """
    Calculate single isochrone.
    """

    isochrone = await crud.isochrone.calculate_single_isochrone(db=db, obj_in=isochrone_in)
    return isochrone


@router.post("/multi", response_model=IsochroneMultiCollection)
async def calculate_multi_isochrone(
    *,
    db: AsyncSession = Depends(deps.get_db),
    isochrone_in: IsochroneMulti = Body(
        ...,
        examples=request_examples.get("multi"),
    ),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Calculate multi isochrone.
    """

    isochrone = await crud.isochrone.calculate_multi_isochrones(db=db, obj_in=isochrone_in)
    return isochrone


@router.post("/multi/count-pois", response_model=IsochroneMultiCountPoisCollection)
async def count_pois_multi_isochrones(
    *,
    db: AsyncSession = Depends(deps.get_db),
    isochrone_in: IsochroneMultiCountPois = Body(
        ..., example=request_examples["multi_count_pois"]
    ),
    current_user: models.User = Depends(deps.get_current_active_user),
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
    *,
    db: AsyncSession = Depends(deps.get_db),
    isochrone_in: IsochroneExport,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Export isochrones.
    """
    file_response = await crud.isochrone.export_isochrone(db=db, obj_in=isochrone_in)
    return file_response
