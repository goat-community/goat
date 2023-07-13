from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud, schemas
from src.db import models
from src.endpoints.legacy import deps
from src.schemas.organization import request_examples

router = APIRouter()


@router.post("/", response_model=models.Organization)
async def create_organization(
    *,
    db: AsyncSession = Depends(deps.get_db),
    organization_in: schemas.OrganizationCreate = Body(..., example=request_examples["create"]),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new organization.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    organization = await crud.organization.get_by_key(db, key="name", value=organization_in.name)
    if organization:
        raise HTTPException(
            status_code=400,
            detail="The organization with this name already exists in the system.",
        )
    organization = await crud.organization.create(db, obj_in=organization_in)
    return organization


@router.get("/", response_model=List[models.Organization])
async def read_organizations(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve organizations.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    organizations = await crud.organization.get_multi(db, extra_fields=[models.Organization.users])
    return organizations


@router.get(
    "/{organization_id}/users",
    response_model=List[models.User],
    response_model_exclude={"hashed_password"},
)
async def get_users_for_organization(
    *,
    db: AsyncSession = Depends(deps.get_db),
    organization_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all users for an organization.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    organization = await crud.organization.get(
        db, id=organization_id, extra_fields=[models.Organization.users]
    )
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    users = organization.users
    return users


@router.put("/{organization_id}", response_model=models.Organization)
async def update_organization(
    *,
    db: AsyncSession = Depends(deps.get_db),
    organization_id: int,
    organization_in: schemas.OrganizationUpdate = Body(..., example=request_examples["update"]),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an organization.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    organization = await crud.organization.get(db, id=organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    organization = await crud.organization.update(
        db, db_obj=organization, obj_in=jsonable_encoder(organization_in)
    )
    return organization


@router.delete("/{organization_id}", response_model=models.Organization)
async def delete_organization(
    *,
    db: AsyncSession = Depends(deps.get_db),
    organization_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an organization.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    organization = await crud.organization.get(db, id=organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    organization = await crud.organization.remove(db, id=organization_id)
    return organization
