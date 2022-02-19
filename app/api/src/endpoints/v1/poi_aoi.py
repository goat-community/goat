import geobuf
from typing import Any

from fastapi import APIRouter, Body, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

from src import crud
from src.db import models
from src.endpoints import deps
from src.schemas.poi_aoi import POIAOIVisualization, request_examples
from src.utils import return_geojson_or_geobuf


router = APIRouter()

@router.post("/visualization/", response_model=Any)
async def poi_aoi_visualization(
    return_type: str = 'geojson',
    db: AsyncSession = Depends(deps.get_db),
    obj_in: POIAOIVisualization = Body(..., example=request_examples["poi_aoi_visualization"]),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Visualize POIs and AOIs based on settings specified by the user.
    """

    obj_in.active_study_area_id = current_user.active_study_area_id

    pois = await crud.poi_aoi.poi_aoi_visualization(db=db, obj_in=obj_in, current_user=current_user, return_type=return_type)
    
    return return_geojson_or_geobuf(pois, return_type)
