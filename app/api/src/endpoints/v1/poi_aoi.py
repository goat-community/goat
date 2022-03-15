from typing import Any, Optional
from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.ext.asyncio.session import AsyncSession

from src import crud
from src.db import models
from src.endpoints import deps
from src.resources.enums import ReturnType
from src.utils import return_geojson_or_geobuf
from src.resources.enums import CalculationTypes

router = APIRouter()

@router.get("/visualization/", response_model=Any)
async def poi_aoi_visualization(
    return_type: ReturnType,
    modus: CalculationTypes,
    scenario_id: Optional[int] = Query(
        description="The scenario id to get the POIs in case the modus is 'scenario' or 'comparison'.",
        default=0,
        example=1
    ),
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Visualize POIs and AOIs based on settings specified by the user.
    """

    pois = await crud.poi_aoi.poi_aoi_visualization(db=db, scenario_id=scenario_id, modus=modus, current_user=current_user, return_type=return_type)
    
    return return_geojson_or_geobuf(pois, return_type)
  