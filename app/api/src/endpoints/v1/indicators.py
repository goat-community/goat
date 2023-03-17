import json
import time
from typing import Any, List, Optional, Union

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, text
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

from src import crud
from src.crud.base import CRUDBase
from src.db import models
from src.db.models.config_validation import HeatmapConfiguration, check_dict_schema
from src.endpoints import deps
from src.resources.enums import (
    AccessibilityHeatmapTypes,
    CalculationTypes,
    ReturnType,
    SQLReturnTypes,
)
from src.schemas.heatmap import HeatmapSettings, ReturnTypeHeatmap
from src.schemas.workers import TaskResultRequest
from src.schemas.heatmap import request_examples as heatmap_request_examples
from src.schemas.heatmap import request_examples_
from src.schemas.indicators import (
    CalculateLocalAccessibilityAggregated,
    CalculateOevGueteklassenParameters,
    local_accessibility_aggregated_example,
    oev_gueteklasse_config_example,
)
from src.utils import return_geojson_or_geobuf
from src.workers.read_heatmap import read_heatmap_task
from src.workers.celery_app import celery_app
from celery.result import AsyncResult

router = APIRouter()


@router.post("/heatmap")
async def calculate_heatmap(
    *,
    # db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    heatmap_settings: HeatmapSettings = Body(..., examples=heatmap_request_examples),
    # return_type: ReturnTypeHeatmap = Query(..., description="Return type of the response"),
):
    """
    Calculate a heatmap.
    """
    current_user = json.loads(current_user.json())
    heatmap_settings = json.loads(heatmap_settings.json())
    task = read_heatmap_task.delay(
        current_user=current_user,
        heatmap_settings=heatmap_settings,
    )
    return {"task_id": task.id}
    

@router.get("/connectivity", response_class=JSONResponse)
async def read_connectivity_heatmap(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    return_type: ReturnType = Query(
        description="Return type of the response", default=ReturnType.geojson
    ),
) -> Any:
    """
    Retrieve the connectivity heatmap.
    """
    _return_type = return_type.value
    if return_type == ReturnType.geobuf.value:
        _return_type = "db_geobuf"  # workaround for the db_geobuf return type
    template_sql = SQLReturnTypes[_return_type].value
    heatmap = await db.execute(
        text(
            template_sql
            % """
            SELECT g.id AS grid_visualization_id, ntile(5) over (order by g.area_isochrone) AS percentile_area_isochrone, 
            g.area_isochrone, 'default' AS modus, g.geom  
            FROM basic.grid_visualization g, basic.study_area_grid_visualization s 
            WHERE g.id = s.grid_visualization_id
            AND s.study_area_id = :active_study_area_id
            AND g.area_isochrone IS NOT NULL
            UNION ALL
            SELECT g.id AS grid_visualization_id, 0 AS percentile_area_isochrone,
            g.area_isochrone, 'default' AS modus, g.geom  
            FROM basic.grid_visualization g, basic.study_area_grid_visualization s 
            WHERE g.id = s.grid_visualization_id
            AND s.study_area_id = :active_study_area_id
            AND g.area_isochrone IS NULL
            """
        ),
        {"active_study_area_id": current_user.active_study_area_id},
    )

    heatmap = heatmap.fetchall()[0][0]
    return return_geojson_or_geobuf(heatmap, _return_type)


@router.get("/population", response_class=JSONResponse)
async def read_population_heatmap(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    modus: CalculationTypes,
    scenario_id: Optional[int] = Query(
        description="The scenario id to calculate the heatmap in case the modus is 'scenario' or 'comparison'",
        default=0,
        example=1,
    ),
    return_type: ReturnType = Query(
        description="Return type of the response", default=ReturnType.geojson
    ),
) -> Any:
    """
    Retrieve the population heatmap.
    """
    _return_type = return_type.value
    if return_type == ReturnType.geobuf.value:
        _return_type = "db_geobuf"
    scenario_id = await deps.check_user_owns_scenario(
        db=db, current_user=current_user, scenario_id=scenario_id
    )
    template_sql = SQLReturnTypes[_return_type].value
    heatmap = await db.execute(
        text(
            template_sql
            % """
            SELECT * FROM basic.heatmap_population(:active_study_area_id, :modus, :scenario_id)
            """
        ),
        {
            "active_study_area_id": current_user.active_study_area_id,
            "modus": modus.value,
            "scenario_id": scenario_id,
        },
    )
    heatmap = heatmap.fetchall()[0][0]
    return return_geojson_or_geobuf(heatmap, _return_type)


@router.get("/local-accessibility", response_class=JSONResponse)
async def read_local_accessibility_heatmap(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    heatmap_type: AccessibilityHeatmapTypes,
    modus: CalculationTypes,
    scenario_id: Optional[int] = Query(
        description="The scenario id to calculate the heatmap in case the modus is 'scenario' or 'comparison'",
        default=0,
        example=1,
    ),
    heatmap_configuration: str = Query(
        ...,
        description="The configuration per POI category to create the dynamic heatmap.",
        example=request_examples_["heatmap_configuration"],
    ),
    return_type: ReturnType = Query(
        description="Return type of the response", default=ReturnType.geojson
    ),
) -> Any:
    """
    Retrieve the local accessibility heatmap.
    """
    _return_type = return_type.value
    if return_type == ReturnType.geobuf.value:
        _return_type = "db_geobuf"
    scenario_id = await deps.check_user_owns_scenario(
        db=db, current_user=current_user, scenario_id=scenario_id
    )
    if check_dict_schema(HeatmapConfiguration, json.loads(heatmap_configuration)) == False:
        raise HTTPException(status_code=400, detail="Heatmap configuration is not valid.")

    active_data_uploads_study_area = await db.execute(
        func.basic.active_data_uploads_study_area(current_user.id)
    )
    active_data_uploads_study_area = active_data_uploads_study_area.scalar()
    if active_data_uploads_study_area == None:
        active_data_uploads_study_area = []

    query_params = {
        "heatmap_configuration": heatmap_configuration,
        "user_id": current_user.id,
        "active_study_area_id": current_user.active_study_area_id,
        "modus": modus.value,
        "scenario_id": scenario_id,
        "data_upload_ids": active_data_uploads_study_area,
    }
    template_sql = SQLReturnTypes[_return_type].value

    heatmap = await db.execute(
        text(
            template_sql
            % f"""
            SELECT * 
            FROM basic.{heatmap_type.value}((:heatmap_configuration)::jsonb, :user_id, :active_study_area_id, :modus, :scenario_id, :data_upload_ids)
            """
        ),
        query_params,
    )
    heatmap = heatmap.fetchall()[0][0]
    return return_geojson_or_geobuf(heatmap, _return_type)


@router.get("/compute/data-upload", response_class=JSONResponse)
async def compute_reached_pois_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    id: List[int] = Query(
        description="The data upload ids to calculate the heatmap in case the modus is 'scenario' or 'comparison'",
        default=0,
        example=[1, 2],
    ),
) -> Any:
    """
    Calculate reached pois for the heatmap for the passed data upload.
    """
    for data_upload_id in id:
        await crud.indicator.compute_reached_pois_user(db, current_user, data_upload_id)
    return {"msg": "Successfully computed heatmap for uploaded pois."}


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
    return_type: ReturnType = Query(
        default=ReturnType.geojson, description="Return type of the response"
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

    stations_count = await crud.indicator.count_pt_service_stations(
        db=db,
        start_time=start_time,
        end_time=end_time,
        weekday=weekday,
        study_area_id=study_area_id,
        return_type=return_type,
    )
    return return_geojson_or_geobuf(stations_count, return_type.value)


@router.post("/pt-oev-gueteklassen")
async def calculate_oev_gueteklassen(
    *,
    db: AsyncSession = Depends(deps.get_db),
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

    oev_gueteklassen_features = await crud.indicator.compute_oev_gueteklassen(
        db=db,
        start_time=params.start_time,
        end_time=params.end_time,
        weekday=params.weekday,
        study_area_ids=study_area_ids,
        station_config=params.station_config,
    )
    if params.return_type.value == ReturnType.geojson.value:
        oev_gueteklassen_features = jsonable_encoder(oev_gueteklassen_features)
    return return_geojson_or_geobuf(oev_gueteklassen_features, params.return_type.value)


@router.post("/local-accessibility-aggregated")
async def calculate_local_accessibility_aggregated(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    params: CalculateLocalAccessibilityAggregated = Body(
        ..., example=local_accessibility_aggregated_example
    ),
):
    """
    Local accessibility aggregated is an indicator.
    """
    # TODO: Check if user owns study area

    # local_accessibility_features = await crud.indicator.compute_local_accessibility_aggregated(
    #     db=db,
    #     study_area_id=study_area_id,
    #     indicator_config=indicator_config
    # )

    return {"Test": "Test"}


@router.get("/ptal")
async def calculate_ptal(
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    PTAL
    """
    return ""



@router.get("/heatmap/result/{task_id}")
async def get_heatmap_result(
    task_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
    return_type: ReturnTypeHeatmap = Query(..., description="Return type of the response"),
):
    """Fetch result for given task_id"""
    result = AsyncResult(task_id, app=celery_app)
    if result.ready():
        try:
            result = None
            if return_type.value == "geobuf":
                result = return_geojson_or_geobuf(result.get(), "geobuf")
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
    