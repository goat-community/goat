from typing import Any, Dict

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse
import json
import binascii
from src import crud
from src.workers.isochrone import task_calculate_isochrone
from src.db import models
from src.endpoints.legacy import deps
from src.resources.enums import IsochroneExportType
from src.schemas.isochrone import (
    IsochroneDTO,
    IsochroneMultiCountPois,
    request_examples,
)

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

    study_area = await crud.user.get_active_study_area(db, current_user)
    study_area_bounds = study_area["bounds"]
    isochrone_in = json.loads(isochrone_in.json())
    current_user = json.loads(current_user.json())

    task = task_calculate_isochrone.delay(isochrone_in, current_user, study_area_bounds)
    return {"task_id": task.id}


@router.get("/task/{task_id}")
async def get_task(
    task_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    task = task_calculate_isochrone.AsyncResult(task_id)
    if task.ready():
        try:
            result = task.get()
            response = Response(
                bytes(binascii.unhexlify(bytes(result, "utf-8"))),
                media_type="application/octet-stream",
            )
            return response
        except Exception:
            raise HTTPException(status_code=500, detail="Task failed")

    elif task.failed():
        raise HTTPException(status_code=500, detail="Task failed")
    else:
        content = {
            "task-status": task.status,
            "details": "Task is still running, please try again later",
        }
        return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=content)


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
