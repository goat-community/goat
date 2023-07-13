from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio.session import AsyncSession

from src import crud
from src.db import models
from src.endpoints.legacy import deps
from src.resources.enums import ReturnType
from src.utils import return_geojson_or_geobuf

router = APIRouter()


@router.get("/visualization", response_model=Any)
async def poi_aoi_visualization(
    return_type: ReturnType,
    scenario_id: Optional[int] = Query(
        description="The scenario id to get the POIs in case the modus is 'scenario' or 'comparison'.",
        default=0,
        example=1,
    ),
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Visualize POIs and AOIs based on settings specified by the user.
    """
    scenario_id = await deps.check_user_owns_scenario(db, scenario_id, current_user)
    pois = await crud.poi_aoi.poi_aoi_visualization(
        db=db, scenario_id=scenario_id, current_user=current_user, return_type=return_type
    )
    _return_type = return_type.value
    if return_type == ReturnType.geobuf.value:
        _return_type = "db_geobuf"
    return return_geojson_or_geobuf(pois, _return_type)
