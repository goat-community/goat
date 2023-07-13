from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud, schemas
from src.db import models
from src.endpoints.legacy import deps

router = APIRouter()


@router.get("", response_model=List[models.OpportunityStudyAreaConfig])
async def list_opportunity_study_area_configs(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_super_user: models.User = Depends(deps.get_current_active_superuser),
):
    opportunities = await crud.opportunity_study_area_config.get_multi(db, skip=skip, limit=limit)
    if not opportunities:
        raise HTTPException(status_code=404, detail="there is no (more) opportunities.")
    return opportunities


@router.get("/{id:int}", response_model=List[models.OpportunityStudyAreaConfig])
async def read_opportunity_study_area_config_by_id(
    id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_super_user: models.User = Depends(deps.get_current_active_superuser),
):
    opportunity = await crud.opportunity_study_area_config.get_multi_by_key(
        db, key="study_area_id", value=id
    )
    if not opportunity:
        raise HTTPException(status_code=404, detail="opportunity not found.")
    return opportunity


@router.post("", response_model=models.OpportunityStudyAreaConfig)
async def create_a_new_opportunity_study_area_config(
    opportunity_in: schemas.CreateOpportunityStudyAreaConfig,
    db: AsyncSession = Depends(deps.get_db),
    current_super_user: models.User = Depends(deps.get_current_active_superuser),
):
    opportunity = await crud.opportunity_study_area_config.create(db, obj_in=opportunity_in)
    return opportunity


@router.put("/{id:int}", response_model=models.OpportunityStudyAreaConfig)
async def update_an_opportunity_study_area_config(
    id: int,
    opportunity_in: schemas.CreateOpportunityStudyAreaConfig,
    db: AsyncSession = Depends(deps.get_db),
    current_super_user: models.User = Depends(deps.get_current_active_superuser),
):
    opportunity_in_db = await crud.opportunity_study_area_config.get(db, id=id)
    if not opportunity_in_db:
        raise HTTPException(status_code=404, detail="opportunity not found.")

    opportunity = await crud.opportunity_study_area_config.update(
        db, db_obj=opportunity_in_db, obj_in=opportunity_in
    )
    return opportunity


@router.delete("/{id:int}", response_model=models.OpportunityStudyAreaConfig)
async def delete_an_opportunity_study_area_config(
    id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_super_user: models.User = Depends(deps.get_current_active_superuser),
):
    opportunity = await crud.opportunity_study_area_config.get(db, id=id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="opportunity not found.")

    opportunity = await crud.opportunity_study_area_config.remove(db, id=opportunity.id)
    return opportunity
