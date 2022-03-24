import json
from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

from src import crud, schemas
from src.db import models
from src.db.models.config_validation import HeatmapConfiguration, check_dict_schema
from src.endpoints import deps
from src.resources.enums import (
    AccessibilityHeatmapTypes,
    CalculationTypes,
    ReturnType,
    SQLReturnTypes,
)
from src.schemas.heatmap import request_examples
from src.utils import return_geojson_or_geobuf

router = APIRouter()


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

    template_sql = SQLReturnTypes[return_type.value].value
    heatmap = await db.execute(
        text(
            template_sql
            % """
            SELECT g.id AS grid_visualization_id, g.percentile_area_isochrone, g.area_isochrone, 'default' AS modus, g.geom  
            FROM basic.grid_visualization g, basic.study_area_grid_visualization s 
            WHERE g.id = s.grid_visualization_id
            AND s.study_area_id = :active_study_area_id
            """
        ),
        {"active_study_area_id": current_user.active_study_area_id},
    )
    heatmap = heatmap.fetchall()[0][0]
    return return_geojson_or_geobuf(heatmap, return_type.value)


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
    scenario_id = await deps.check_user_owns_scenario(
        db=db, current_user=current_user, scenario_id=scenario_id
    )

    template_sql = SQLReturnTypes[return_type.value].value
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
    return return_geojson_or_geobuf(heatmap, return_type.value)


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
        example=request_examples["heatmap_configuration"],
    ),
    return_type: ReturnType = Query(
        description="Return type of the response", default=ReturnType.geojson
    ),
) -> Any:
    """
    Retrieve the local accessibility heatmap.
    """
    scenario_id = await deps.check_user_owns_scenario(
        db=db, current_user=current_user, scenario_id=scenario_id
    )

    if check_dict_schema(HeatmapConfiguration, json.loads(heatmap_configuration)) == False:
        raise HTTPException(status_code=400, detail="Heatmap configuration is not valid.")

    query_params = {
        "heatmap_configuration": heatmap_configuration,
        "user_id": current_user.id,
        "active_study_area_id": current_user.active_study_area_id,
        "modus": modus.value,
        "scenario_id": scenario_id,
        "data_upload_ids": current_user.active_data_upload_ids,
    }
    template_sql = SQLReturnTypes[return_type.value].value

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
    return return_geojson_or_geobuf(heatmap, return_type.value)


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
