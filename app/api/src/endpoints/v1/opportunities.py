from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src.db import models
from src.endpoints.legacy import deps

router = APIRouter()


@router.get("", response_model=List[models.OpportunityDefaultConfig])
async def list_opportunities(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    opportunities = await crud.opportunity_default_config.get_multi(db, skip=skip, limit=limit)
    if not opportunities:
        raise HTTPException(status_code=404, detail="there is no (more) opportunities.")
    return opportunities


@router.get("/groups", response_model=List[models.OpportunityGroup])
async def list_opportunity_groups(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    groups = await crud.opportunity_group.get_multi(db, skip=skip, limit=limit)
    if not groups:
        raise HTTPException(status_code=404, detail="there is no (more) groups.")
    return groups
