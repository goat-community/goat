import json
from typing import Any

from fastapi import APIRouter, Body, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

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
    IsochronePoiMulti,
    request_examples,
)

router = APIRouter()


@router.post("/single", response_class=JSONResponse)
async def calculate_single_isochrone(
    *,
    db: AsyncSession = Depends(deps.get_db),
    isochrone_in: IsochroneSingle = Body(..., example=request_examples["single_isochrone"]),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Calculate single isochrone.
    """
    isochrone_in.user_id = current_user.id
    isochrone = await crud.isochrone.calculate_single_isochrone(db=db, obj_in=isochrone_in)
    return json.loads(isochrone.to_json()) 

@router.post("/network", response_model=Any)
async def calculate_reached_network(
    *, db: AsyncSession = Depends(deps.get_db), isochrone_in: IsochroneSingle
) -> Any:
    """
    Calculate the reached network for a single isochrone.
    """

    network = await crud.isochrone.calculate_reached_network(db=db, obj_in=isochrone_in)
    return network


@router.post("/multi", response_class=JSONResponse)
async def calculate_multi_isochrone(
    *,
    db: AsyncSession = Depends(deps.get_db),
    isochrone_in: IsochroneMulti = Body(...,example=request_examples["multi_isochrone"]),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Calculate multi isochrone.
    """
    isochrone_in.user_id = current_user.id
    isochrone = await crud.isochrone.calculate_multi_isochrones(db=db, obj_in=isochrone_in)
    return json.loads(isochrone.to_json())


@router.post("/multi/count-pois", response_model=IsochroneMultiCountPoisCollection)
async def count_pois_multi_isochrones(
    *,
    db: AsyncSession = Depends(deps.get_db),
    isochrone_in: IsochroneMultiCountPois = Body(
        ..., example=request_examples["pois_multi_isochrone_count_pois"]
    ),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Count pois under study area.
    """
    isochrone_in.user_id = current_user.id
    feature_collection = await crud.isochrone.count_pois_multi_isochrones(
        db=db, obj_in=isochrone_in
    )
    return feature_collection

@router.post("/multi/pois", response_class=JSONResponse)
async def poi_multi_isochrones(
    *,
    db: AsyncSession = Depends(deps.get_db),
    isochrone_in: IsochronePoiMulti = Body(
        ..., examples=request_examples.get("pois_multi_isochrone_study_area")
    ),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Compute multiisochrone with POIs as starting points.
    """
    isochrone_in.user_id = current_user.id
    gdf = await crud.isochrone.calculate_pois_multi_isochrones(
        db=db, obj_in=isochrone_in
    )
    return json.loads(gdf.to_json())


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
