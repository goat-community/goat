import json
from typing import Any, Dict

import pandas as pd
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from fastapi.responses import StreamingResponse
from geopandas import GeoDataFrame
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

from src import crud, schemas
from src.db import models
from src.endpoints import deps
from src.resources.enums import (
    CalculationTypes,
    IsochroneExportType,
    ReturnWithoutDbGeobufEnum,
)
from src.schemas import isochrone
from src.schemas.isochrone import (
    IsochroneDTO,
    IsochroneMulti,
    IsochroneMultiCountPois,
    IsochronePoiMulti,
    IsochroneSingle,
    request_examples,
)
from src.utils import return_geojson_or_geobuf

router = APIRouter()


@router.post("")
async def calculate_isochrone(
    *,
    db: AsyncSession = Depends(deps.get_db),
    isochrone_in: IsochroneDTO = Body(..., examples=request_examples["isochrone"]),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Calculate isochrone.
    """
    if isochrone_in.scenario.id:
        await deps.check_user_owns_scenario(db, isochrone_in.scenario.id, current_user)
    result = await crud.isochrone.calculate(db, isochrone_in, current_user)
    return result


@router.post("/multi/count-pois", response_class=JSONResponse)
async def count_pois_multi_isochrones(
    *,
    db: AsyncSession = Depends(deps.get_db),
    isochrone_in: IsochroneMultiCountPois = Body(
        ..., examples=request_examples["pois_multi_isochrone_count_pois"]
    ),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Count pois under study area.
    """
    isochrone_in.scenario_id = await deps.check_user_owns_scenario(
        db=db, scenario_id=isochrone_in.scenario_id, current_user=current_user
    )
    isochrone_in.active_upload_ids = current_user.active_data_upload_ids
    isochrone_in.user_id = current_user.id
    cnt = await crud.isochrone.count_opportunity(db=db, obj_in=isochrone_in)
    return cnt


@router.post("/export", response_class=StreamingResponse)
async def export_isochrones(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    geojson: Dict = Body(..., example=request_examples["geojson_to_export"]),
    return_type: IsochroneExportType = Query(
        description="Return type of the response", default=IsochroneExportType.geojson
    ),
) -> Any:
    """
    Export isochrones from GeoJSON data.
    """

    file_response = await crud.isochrone.export_isochrone(
        db=db,
        current_user=current_user,
        return_type=return_type.value,
        geojson_dictionary=geojson,
    )
    return file_response
