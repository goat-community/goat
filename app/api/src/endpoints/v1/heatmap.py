import json
from typing import Any

from fastapi import APIRouter, Body, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

from src import crud, schemas
from src.db import models
from src.endpoints import deps
from src.schemas.heatmap import request_examples

router = APIRouter()


@router.get("/compute/data_upload/{data_upload_id}", response_class=JSONResponse)
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
