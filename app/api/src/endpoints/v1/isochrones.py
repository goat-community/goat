import json
from typing import Any

from fastapi import APIRouter, Body, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

from src import crud, schemas
from src.db import models
from src.endpoints import deps
from src.schemas.isochrone import (
    IsochroneExport,
    IsochroneMulti,
    IsochroneMultiCollection,
    IsochroneMultiCountPois,
    IsochroneMultiCountPoisCollection,
    IsochronePoiMulti,
    IsochroneSingle,
    IsochroneSingleCollection,
    request_examples,
)
from src.utils import return_geojson_or_geobuf

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


@router.get(
    "/network/{isochrone_calculation_id}/{modus}/{return_type}", response_class=JSONResponse
)
async def calculate_reached_network(
    *,
    db: AsyncSession = Depends(deps.get_db),
    isochrone_calculation_id: int,
    modus: str = "default",
    return_type: str = "geobuf",
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Calculate the reached network for a single isochrone.
    """
    isochrone_calc_obj = await crud.isochrone_calculation.get_by_key(
        db=db, key="id", value=isochrone_calculation_id
    )
    isochrone_calc_obj = isochrone_calc_obj[0]
    isochrone_feature_obj = await crud.isochrone_feature.get_by_key(
        db=db, key="isochrone_calculation_id", value=isochrone_calculation_id
    )

    minutes = int(max([obj.step for obj in isochrone_feature_obj]) / 60)

    x, y = isochrone_calc_obj.starting_point.replace("POINT (", "").replace(")", "").split(" ")

    obj_calculation = IsochroneSingle(
        minutes=minutes,
        speed=3.6 * isochrone_calc_obj.speed,
        n=len(isochrone_feature_obj),
        modus=modus,
        x=x,
        y=y,
        user_id=current_user.id,
        routing_profile=isochrone_calc_obj.routing_profile,
        active_upload_ids=current_user.active_data_upload_ids,
        scenario_id=isochrone_calc_obj.scenario_id,
    )

    network = await crud.isochrone.calculate_reached_network(db=db, obj_in=obj_calculation)
    return return_geojson_or_geobuf(json.JSONDecoder().decode(json.dumps(network)), return_type)


@router.post("/multi", response_class=JSONResponse)
async def calculate_multi_isochrone(
    *,
    db: AsyncSession = Depends(deps.get_db),
    isochrone_in: IsochroneMulti = Body(..., example=request_examples["multi_isochrone"]),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Calculate multi isochrone.
    """
    isochrone_in.user_id = current_user.id
    isochrone = await crud.isochrone.calculate_multi_isochrones(db=db, obj_in=isochrone_in)
    return json.loads(isochrone.to_json())


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
    isochrone_in.user_id = current_user.id
    cnt = await crud.isochrone.count_pois_multi_isochrones(db=db, obj_in=isochrone_in)
    return cnt


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
    gdf = await crud.isochrone.calculate_pois_multi_isochrones(db=db, obj_in=isochrone_in)
    return json.loads(gdf.to_json())


@router.post("/export/", response_class=StreamingResponse)
async def export_isochrones(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    obj_in: schemas.isochrone.IsochroneExport = Body(
        ..., example=request_examples["export_isochrones"]
    )
) -> Any:
    """
    Export isochrones.
    """

    file_response = await crud.isochrone.export_isochrone(db=db, current_user=current_user, isochrone_calculation_id=obj_in.isochrone_calculation_id, return_type=obj_in.return_type)
    return file_response
