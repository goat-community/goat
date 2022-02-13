from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src.db import models
from src.endpoints import deps

router = APIRouter()


@router.get("/{user_id}", response_class=JSONResponse)
async def get_user_settings(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get customization settings for user.
    """
    is_superuser = crud.user.is_superuser(user=current_user)
    if user_id != current_user.id and not is_superuser:
        raise HTTPException(status_code=400, detail="The user cannot get another user's settings")
    customizations = await crud.customization.get_multi(db)
    settings = {}
    for customization in customizations:
        settings.update(customization.default_setting)
    user_customizations = await crud.customization.get_user_customization(db, user_id=user_id)
    for user_customization in user_customizations:
        settings.update(user_customization.setting)

    user = await crud.user.get(db, id=user_id, extra_fields=[models.User.user_customizations])
    return settings


# update user customization
@router.post("/{user_id}", response_class=JSONResponse)
async def update_user_settings(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    user_customization: Any,
) -> Any:
    """
    Update customization settings for user.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if user_id != current_user.id and not is_superuser:
        raise HTTPException(
            status_code=400, detail="The user cannot update another user's settings"
        )
