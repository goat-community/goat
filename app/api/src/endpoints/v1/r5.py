from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio.session import AsyncSession

from src import crud
from src.db import models
from src.endpoints import deps
from src.resources.enums import ReturnType
from src.schemas.r5 import R5RegionCreateDTO, R5RegionInDB, request_examples
from src.utils import return_geojson_or_geobuf

router = APIRouter()


@router.get("/regions", response_model=List[R5RegionInDB])
async def get_regions(
    *,
    db: AsyncSession = Depends(deps.get_r5_mongo_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all regions.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    regions = await crud.r5.get_all_regions(db)
    return regions


@router.post("/regions", response_model=R5RegionInDB)
async def region_create(
    *,
    db: AsyncSession = Depends(deps.get_r5_mongo_db),
    region_in: R5RegionCreateDTO = Body(..., example=request_examples["region"]["create"]),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new region.
    """
    region = await crud.r5.create_region(db=db, region_in=region_in, current_user=current_user)

    return region
