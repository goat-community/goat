from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud, schemas
from src.crud.base import CRUDBase
from src.db import models
from src.endpoints import deps

router = APIRouter()


@router.get("/me", response_class=JSONResponse)
async def get_user_settings_me(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get customization settings for user.
    """
    customizations = await crud.customization.get_multi(db)
    settings = {}
    for customization in customizations:
        settings.update(customization.default_setting)
    user_customizations = await CRUDBase(models.UserCustomization).get_by_key(
        db, key="user_id", value=current_user.id
    )
    study_area = await CRUDBase(models.StudyArea).get(db, id=current_user.active_study_area_id)
    if study_area is not None and study_area.default_setting:
        settings.update(study_area.default_setting)

    if user_customizations is not None:
        for user_customization in user_customizations:
            settings.update(user_customization.setting)

    return settings


@router.get("/{user_id}/{study_area_id}", response_class=JSONResponse)
async def get_user_settings(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: int,
    study_area_id: int = None,
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
    user_customizations = await CRUDBase(models.UserCustomization).get_by_key(
        db, key="user_id", value=user_id
    )
    study_area = await CRUDBase(models.StudyArea).get(db, id=study_area_id)
    if study_area is not None and study_area.default_setting:
        settings.update(study_area.default_setting)

    if user_customizations is not None:
        for user_customization in user_customizations:
            settings.update(user_customization.setting)

    return settings


# create user customization
@router.post("/{user_id}/{study_area_id}", response_class=JSONResponse)
async def update_user_settings(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: int,
    study_area_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    user_customizations: Any = Body(..., example=schemas.customization.request_examples["create"]),
) -> Any:
    """
    Create or Update customization settings for user.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if user_id != current_user.id and not is_superuser:
        raise HTTPException(
            status_code=400, detail="The user cannot update another user's settings"
        )
    for user_customization_key in user_customizations:
        # check if key exists in customization table
        customization = await CRUDBase(models.Customization).get_by_key(
            db, key="type", value=user_customization_key
        )
        
        if customization is not None:
            customization = customization[0]
            user_customization = await CRUDBase(models.UserCustomization).get_by_multi_keys(
                db, keys={"user_id": user_id, "customization_id": customization.id}
            )
            user_customization_in = models.UserCustomization(
                setting=user_customizations[user_customization_key],
                user_id=user_id,
                customization_id=customization.id,
            )
            if user_customization is not None and len(user_customization) > 0:
                del user_customization_in.id
                del user_customization_in.creation_date
                await CRUDBase(models.UserCustomization).update(
                    db, db_obj=user_customization[0], obj_in=user_customization_in
                )
            else:
                await CRUDBase(models.UserCustomization).create(db, obj_in=user_customization_in)

    return {"msg": "ok"}


# delete user customization
@router.delete("/{user_id}/{study_area_id}/{customization}", response_class=JSONResponse)
async def delete_user_setting(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: int,
    study_area_id: int,
    customization: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete customization for user.
    """
    is_superuser = crud.user.is_superuser(current_user)
    if user_id != current_user.id and not is_superuser:
        raise HTTPException(
            status_code=400, detail="The user cannot delete another user's settings"
        )
    customization = await CRUDBase(models.Customization).get_by_key(
        db, key="type", value=customization
    )
    if customization is None:
        raise HTTPException(status_code=400, detail="Customization not found")
    else:
        customization = customization[0]

    user_customization = await CRUDBase(models.UserCustomization).get_by_multi_keys(
        db, keys={"user_id": user_id, "customization_id": customization.id}
    )

    if user_customization is not None and len(user_customization) > 0:
        await CRUDBase(models.UserCustomization).remove(db, id=user_customization[0].id)
    return {"msg": "Customization deleted"}
