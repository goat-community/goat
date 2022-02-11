from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud, schemas
from src.db import models
from src.endpoints import deps
from src.schemas.organization import request_examples

router = APIRouter()


@router.get("/", response_model=List[models.Organization])
async def read_organizations(db: AsyncSession = Depends(deps.get_db)) -> Any:
    """
    Retrieve organizations.
    """
    organizations = await crud.organization.get_multi(db)
    return organizations


@router.post("/", response_model=models.Organization)
async def create_organization(
    *,
    db: AsyncSession = Depends(deps.get_db),
    organization_in: schemas.OrganizationCreate = Body(..., example=request_examples["create"]),
) -> Any:
    """
    Create new organization.
    """
    organization = await crud.organization.get_by_name(db, name=organization_in.name)
    if organization:
        raise HTTPException(
            status_code=400,
            detail="The organization with this name already exists in the system.",
        )
    organization = await crud.organization.create(db, obj_in=jsonable_encoder(organization_in))
    return organization
