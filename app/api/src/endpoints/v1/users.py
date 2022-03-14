import json
from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic.networks import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud, schemas
from src.core.config import settings
from src.crud.base import CRUDBase
from src.db import models
from src.endpoints import deps
from src.schemas.user import request_examples
from src.utils import send_new_account_email, to_feature_collection

router = APIRouter()


@router.get("/", response_model=List[models.User], response_model_exclude={"hashed_password"})
async def read_users(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve users.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    users = await crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.get("/me", response_model=models.User, response_model_exclude={"hashed_password"})
async def read_user_me(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


# get user active study area
@router.get("/me/study-area", response_class=JSONResponse)
async def read_user_study_area(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user's active study area.
    """
    study_area = await crud.user.get_active_study_area(db, current_user)

    features = to_feature_collection(
        study_area, exclude_properties=["default_setting", "buffer_geom_heatmap"]
    )
    return features


# get user study areas
@router.get(
    "/me/study-areas-list",
    response_model=List[models.StudyArea],
    response_model_exclude={"geom", "buffer_geom_heatmap", "default_setting", "population"},
)
async def read_user_study_areas(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get user study areas.
    """
    user = await crud.user.get(db, id=current_user.id, extra_fields=[models.User.study_areas])
    return user.study_areas


@router.post("/", response_model=models.User, response_model_exclude={"hashed_password"})
async def create_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: schemas.UserCreate = Body(..., example=request_examples["create"]),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new user.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    user = await crud.user.get_by_key(db, key="email", value=user_in.email)
    user = user[0]
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = await crud.user.create(db, obj_in=user_in)
    if settings.EMAILS_ENABLED and user_in.email:
        send_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
    return user


@router.get("/{user_id}", response_model=models.User, response_model_exclude={"hashed_password"})
async def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    user = await crud.user.get(db, id=user_id, extra_fields=[models.User.roles])
    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")
    return user


@router.delete(
    "/{user_id}", response_model=models.User, response_model_exclude={"hashed_password"}
)
async def delete_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a user.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = await crud.user.remove(db, id=user_id)
    return user


@router.put("/{user_id}", response_model=models.User, response_model_exclude={"hashed_password"})
async def update_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdate = Body(..., example=request_examples["update"]),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a user.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if not is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")

    user = await crud.user.get(
        db, id=user_id, extra_fields=[models.User.study_areas, models.User.roles]
    )
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = await crud.user.update(db, db_obj=user, obj_in=user_in)
    return user
