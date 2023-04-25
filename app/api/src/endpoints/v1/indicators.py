import json
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

from src import crud
from src.crud.base import CRUDBase
from src.core.config import settings
from src.db import models
from src.endpoints import deps
from src.resources.enums import (
    IsochroneExportType,
    ReturnType,
)
from src.schemas.heatmap import HeatmapSettings
from src.schemas.heatmap import request_examples as heatmap_request_examples
from src.schemas.indicators import (
    CalculateOevGueteklassenParameters,
    oev_gueteklasse_config_example,
)

from src.schemas.isochrone import (
    IsochroneDTO,
    IsochroneMultiCountPois,
    IsochroneOutputType,
    IsochroneTypeEnum,
    request_examples,
)
from src.utils import return_geojson_or_geobuf
from src.workers.method_connector import (
    read_heatmap_async,
    read_pt_oev_gueteklassen_async,
    read_pt_station_count_async,
)
from src.workers.read_heatmap import (
    read_heatmap_task,
    read_pt_oev_gueteklassen_task,
    read_pt_station_count_task,
)
from src.workers.celery_app import celery_app
from celery.result import AsyncResult
from src.schemas.utils import (
    validate_poi_limit_multi_isochrone,
    POIExceededException,
)

router = APIRouter()


@router.post("/isochrone")
async def calculate_isochrone(
    *,
    db: AsyncSession = Depends(deps.get_db),
    isochrone_in: IsochroneDTO = Body(..., examples=request_examples["isochrone"]),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Calculate isochrone indicator.
    """

    if isochrone_in.scenario.id:
        await deps.check_user_owns_scenario(db, isochrone_in.scenario.id, current_user)
    if isochrone_in.origin_type == IsochroneTypeEnum.multi and not crud.user.is_superuser(
        current_user
    ):
        isochorne_multi_count_pois = isochrone_in.to_multi_count_pois()
        isochorne_multi_count_pois.user_id = current_user.id
        isochorne_multi_count_pois.active_upload_ids = current_user.active_data_upload_ids
        try:
            await validate_poi_limit_multi_isochrone(isochorne_multi_count_pois, db)
        except POIExceededException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    result = await crud.isochrone.calculate(db, isochrone_in, current_user)
    if isochrone_in.output.type.value == IsochroneOutputType.NETWORK.value:
        result = return_geojson_or_geobuf(result, "geojson")
    return result


@router.post("/isochrone/multi/count-pois", response_class=JSONResponse)
async def count_pois_multi_isochrones(
    *,
    db: AsyncSession = Depends(deps.get_db),
    isochrone_in: IsochroneMultiCountPois = Body(
        ..., examples=request_examples["pois_multi_isochrone_count_pois"]
    ),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Count Isochrone pois under study area.
    """
    isochrone_in.scenario_id = await deps.check_user_owns_scenario(
        db=db, scenario_id=isochrone_in.scenario_id, current_user=current_user
    )
    isochrone_in.active_upload_ids = current_user.active_data_upload_ids
    isochrone_in.user_id = current_user.id
    cnt = await crud.isochrone.count_opportunity(db=db, obj_in=isochrone_in)
    return cnt


@router.post("/isochrone/export", response_class=StreamingResponse)
async def export_isochrones(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    geojson: Dict = Body(..., examples=request_examples["to_export"]),
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


@router.post("/heatmap")
async def calculate_heatmap(
    *,
    current_user: models.User = Depends(deps.get_current_active_user),
    heatmap_settings: HeatmapSettings = Body(..., examples=heatmap_request_examples),
):
    """
    Calculate a heatmap for a given set of parameters.
    """
    current_user = json.loads(current_user.json())
    heatmap_settings = json.loads(heatmap_settings.json())
    if settings.CELERY_BROKER_URL:
        task = read_heatmap_task.delay(
            current_user=current_user,
            heatmap_settings=heatmap_settings,
        )
    else:
        results = await read_heatmap_async(current_user=current_user, settings=heatmap_settings)
        return return_geojson_or_geobuf(results, return_type="geobuf")
    return {"task_id": task.id}


@router.get("/pt-station-count")
async def count_pt_service_stations(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    start_time: Optional[int] = Query(
        description="Start time in seconds since midnight (Default: 07:00)",
        default=25200,
        ge=0,
        le=86400,
    ),
    end_time: Optional[int] = Query(
        description="End time in seconds since midnight (Default: 09:00)",
        default=32400,
        ge=0,
        le=86400,
    ),
    weekday: Optional[int] = Query(
        description="Weekday (1 = Monday, 7 = Sunday) (Default: Monday)", default=1, ge=1, le=7
    ),
    study_area_id: Optional[int] = Query(
        default=None, description="Study area id (Default: User active study area)"
    ),
):
    """
    Return the number of trips for every route type on every station given a time period and weekday.
    """
    if start_time >= end_time:
        raise HTTPException(status_code=422, detail="Start time must be before end time")

    is_superuser = crud.user.is_superuser(current_user)
    if study_area_id is not None and not is_superuser:
        owns_study_area = await CRUDBase(models.UserStudyArea).get_by_multi_keys(
            db, keys={"user_id": current_user.id, "study_area_id": study_area_id}
        )
        if owns_study_area == []:
            raise HTTPException(
                status_code=400,
                detail="The user doesn't own the study area or user doesn't have enough privileges",
            )
    else:
        study_area_id = study_area_id or current_user.active_study_area_id

    current_user = json.loads(current_user.json())
    payload = {
        "start_time": start_time,
        "end_time": end_time,
        "weekday": weekday,
        "study_area_id": study_area_id,
    }

    if settings.CELERY_BROKER_URL:
        task = read_pt_station_count_task.delay(
            current_user=current_user,
            payload=payload,
        )
    else:
        results = await read_pt_station_count_async(current_user=current_user, payload=payload)
        return return_geojson_or_geobuf(results, return_type="geobuf")
    return {"task_id": task.id}


@router.post("/pt-oev-gueteklassen")
async def calculate_oev_gueteklassen(
    *,
    current_user: models.User = Depends(deps.get_current_active_user),
    params: CalculateOevGueteklassenParameters = Body(..., example=oev_gueteklasse_config_example),
):
    """
    ÖV-Güteklassen (The public transport quality classes) is an indicator for access to public transport.
    The indicator makes it possible to identify locations which, thanks to their good access to public transport, have great potential as focal points for development.
    The calculation in an automated process from the data in the electronic timetable (GTFS).
    """
    if params.start_time >= params.end_time:
        raise HTTPException(status_code=422, detail="Start time must be before end time")

    is_superuser = crud.user.is_superuser(current_user)

    if is_superuser and params.study_area_ids is not None:
        study_area_ids = params.study_area_ids
    elif not is_superuser and params.study_area_ids and len(params.study_area_ids) > 0:
        return HTTPException(
            status_code=400,
            detail="The user doesn't have enough privileges to calculate the indicator for other study areas",
        )
    else:
        study_area_ids = [current_user.active_study_area_id]

    current_user = json.loads(current_user.json())
    payload = json.loads(params.json())
    payload["study_area_ids"] = study_area_ids
    if settings.CELERY_BROKER_URL:
        task = read_pt_oev_gueteklassen_task.delay(
            current_user=current_user,
            payload=payload,
        )
    else:
        results = await read_pt_oev_gueteklassen_async(current_user=current_user, payload=payload)
        return return_geojson_or_geobuf(results, return_type="geobuf")
    return {"task_id": task.id}


@router.get("/result/{task_id}")
async def get_indicators_result(
    task_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
    return_type: ReturnType = Query(..., description="Return type of the response"),
):
    """Fetch result for given task_id"""
    result = AsyncResult(task_id, app=celery_app)
    if result.ready():
        try:
            result = return_geojson_or_geobuf(result.get(), return_type.value)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail="Task failed")

    elif result.failed():
        raise HTTPException(status_code=500, detail="Task failed")
    else:
        content = {
            "task-status": result.status,
            "details": "Task is still running, please try again later",
        }
        return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=content)
