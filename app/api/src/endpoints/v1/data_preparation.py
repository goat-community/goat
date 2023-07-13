import json
import linecache
import os
import tracemalloc

from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.heatmap.heatmap_compute import ComputeHeatmap
from src.db import models
from src.endpoints.legacy import deps
from src.schemas import data_preparation as schemas
from src.workers import heatmap_active_mobility, heatmap_motorized_transport, method_connector

router = APIRouter()


def display_top(snapshot, key_type="lineno", limit=3):
    snapshot = snapshot.filter_traces(
        (
            tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
            tracemalloc.Filter(False, "<unknown>"),
        )
    )
    top_stats = snapshot.statistics(key_type)

    print("Top %s lines" % limit)
    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]
        # replace "/path/to/module/file.py" with "module/file.py"
        filename = os.sep.join(frame.filename.split(os.sep)[-2:])
        print("#%s: %s:%s: %.1f KiB" % (index, filename, frame.lineno, stat.size / 1024))
        line = linecache.getline(frame.filename, frame.lineno).strip()
        if line:
            print("    %s" % line)

    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        print("%s other: %.1f KiB" % (len(other), size / 1024))
    total = sum(stat.size for stat in top_stats)
    print("Total allocated size: %.1f KiB" % (total / 1024))


@router.post("/bulk-ids")
async def get_bulk_ids_for_study_area(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_super_user: models.User = Depends(deps.get_current_active_superuser),
    parameters: schemas.BulkIdParameters = Body(..., example=schemas.BulkIdParametersExample),
):
    crud_compute_heatmap = ComputeHeatmap(current_super_user)
    return await crud_compute_heatmap.get_bulk_ids(**parameters.dict())


@router.post("/traveltime-matrices")
async def create_traveltime_matrices(
    *,
    current_super_user: models.User = Depends(deps.get_current_active_superuser),
    parameters: schemas.TravelTimeMatrixParameters = Body(
        ..., examples=schemas.examples["travel_time_matrix"]
    ),
):
    parameters = json.loads(parameters.json())
    parameters_serialized = parameters.copy()
    current_super_user = json.loads(current_super_user.json())
    for bulk_id in parameters["bulk_id"]:
        parameters_serialized["bulk_id"] = bulk_id
        if settings.CELERY_BROKER_URL:
            if parameters["isochrone_dto"]["mode"] != "transit":
                heatmap_active_mobility.create_traveltime_matrices_sync.delay(
                    current_super_user, parameters_serialized
                )
            else:
                heatmap_motorized_transport.create_r5_traveltime_matrices_sync.delay(
                    current_super_user, parameters_serialized
                )
        else:
            await method_connector.create_traveltime_matrices_async(
                current_super_user, parameters_serialized
            )
    return JSONResponse("Ok")


@router.post("/opportunity-matrices")
async def create_opportunity_matrices(
    *,
    current_super_user: models.User = Depends(deps.get_current_active_superuser),
    parameters: schemas.OpportunityMatrixParameters = Body(
        ..., examples=schemas.examples["opportunity_matrix"]
    ),
):
    parameters = json.loads(parameters.json())
    parameters_serialized = parameters.copy()
    current_super_user = json.loads(current_super_user.json())
    for bulk_id in parameters["bulk_id"]:
        parameters_serialized["bulk_id"] = bulk_id
        if settings.CELERY_BROKER_URL:
            heatmap_active_mobility.create_opportunity_matrices_sync.delay(
                current_super_user, parameters_serialized
            )
        else:
            await method_connector.create_opportunity_matrices_async(
                current_super_user, parameters_serialized
            )
    return JSONResponse("Ok")


@router.post("/connectivity-matrices")
async def create_connectivity_matrices(
    *,
    current_super_user: models.User = Depends(deps.get_current_active_superuser),
    parameters: schemas.ConnectivityMatrixParameters = Body(
        ..., example=schemas.ConnectivityMatrixExample
    ),
):
    parameters = json.loads(parameters.json())
    parameters_serialized = parameters.copy()
    current_super_user = json.loads(current_super_user.json())
    for bulk_id in parameters["bulk_id"]:
        parameters_serialized["bulk_id"] = bulk_id
        if settings.CELERY_BROKER_URL:
            heatmap_active_mobility.create_connectivity_matrices_sync.delay(
                current_super_user, parameters_serialized
            )
        else:
            await method_connector.create_connectivity_matrices_async(
                current_super_user, parameters_serialized
            )

    return JSONResponse("Ok")
