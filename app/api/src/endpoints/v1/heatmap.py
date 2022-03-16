import json
from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse
from sqlalchemy import text
from src import crud, schemas
from src.db import models
from src.db.models.config_validation import HeatmapConfiguration, check_dict_schema
from src.endpoints import deps
from src.resources.enums import CalculationTypes, ReturnType, SQLReturnTypes
from src.schemas.heatmap import request_examples
from src.utils import return_geojson_or_geobuf

router = APIRouter()


@router.get("/compute/data-upload/{data_upload_id}", response_class=JSONResponse)
async def compute_reached_pois_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    data_upload_id: int,
) -> Any:
    """
    Calculate reached pois for the heatmap for the passed data upload.
    """
    await crud.heatmap.compute_reached_pois_user(db, current_user, data_upload_id)
    return {"msg": "Successfully computed heatmap for uploaded pois."}


@router.get("/compute/scenario/{scenario_id}", response_class=JSONResponse)
async def compute_reached_pois_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    scenario_id: int,
) -> Any:
    """
    Calculate reached pois for the heatmap for the passed scenario id.
    """
    await crud.heatmap.compute_reached_pois_scenario(db, current_user, scenario_id)
    return {"msg": "Successfully computed heatmap for uploaded pois."}


@router.get("/local-accessibility/{modus}/", response_class=JSONResponse)
async def read_local_accessibility_heatmap(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    modus: CalculationTypes,
    scenario_id: Optional[int] = Query(
        description="The scenario id to calculate the heatmap for in case the modus is 'scenario' or 'comparison'",
        default=0,
        example=1
    ),
    heatmap_configuration: str = Query(
        ...,
        description="The configuration per POI category to create the dynamic heatmap.",
        example=request_examples["heatmap_configuration"],
    ),
    return_type: ReturnType = Query(
        description="Return type of the response",
        default=ReturnType.geojson
    ),
) -> Any:
    """
    Calculate reached pois for the heatmap for the passed scenario id.
    """
    if scenario_id != 0:
        scenario_id = await deps.check_user_owns_scenario(db=db, current_user=current_user, scenario_id=scenario_id)

    if check_dict_schema(HeatmapConfiguration, json.loads(heatmap_configuration)) == False:
        raise HTTPException(status_code=400, detail="Heatmap configuration is not valid.")

    query_params = {
        "heatmap_configuration": heatmap_configuration,
        "user_id": current_user.id,
        "active_study_area_id": current_user.active_study_area_id,
        "modus": modus.value,
        "scenario_id": scenario_id.id,
        "data_upload_ids": current_user.active_data_upload_ids,
    }
    template_sql = SQLReturnTypes[return_type.value].value

    heatmap = await db.execute(
        text(template_sql % 
            """
            SELECT * 
            FROM basic.heatmap_local_accessibility((:heatmap_configuration)::jsonb, :user_id, :active_study_area_id, :modus, :scenario_id, :data_upload_ids)
            """
        ), query_params
    )
    heatmap = heatmap.fetchall()[0][0]
    return return_geojson_or_geobuf(heatmap, return_type.value)
