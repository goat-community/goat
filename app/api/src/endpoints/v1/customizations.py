from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Path
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud, schemas
from src.crud.base import CRUDBase
from src.crud.crud_customization import dynamic_customization
from src.db import models
from src.db.models.legacy.config_validation import *
from src.endpoints.legacy import deps
from src.resources.enums import SettingToModify
from src.schemas.customization import request_examples

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
    settings = await dynamic_customization.build_main_setting_json(
        db=db, current_user=current_user
    )

    return settings


@router.post("/user/insert/{setting_type}", response_class=JSONResponse)
async def insert_user_settings(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    setting_type: SettingToModify,
    obj_in: Any = Body(..., examples=request_examples.get("user_customization_insert")),
) -> Any:
    """
    Insert settings for POIs.
    """
    obj_dict = jsonable_encoder(obj_in)
    if setting_type.value == "poi_groups":
        if check_dict_schema(PoiCategory, obj_dict) is False:
            raise HTTPException(status_code=400, detail="Invalid JSON-schema")

    await dynamic_customization.insert_opportunity_setting(
        db=db, current_user=current_user, insert_settings=obj_dict
    )

    update_settings = await dynamic_customization.build_main_setting_json(
        db=db, current_user=current_user
    )
    return update_settings


@router.delete("/user/reset-style/{setting_type}/{category}", response_class=JSONResponse)
async def delete_user_settings(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    setting_type: SettingToModify,
    category: str = Path(..., description="Category name", example="nursery"),
) -> Any:
    """
    Reset styles for POIs
    """
    if category not in await crud.dynamic_customization.get_all_default_poi_categories(db=db):
        raise HTTPException(status_code=400, detail="Cannot reset custom POI category.")

    await dynamic_customization.delete_opportunity_setting(
        db=db, current_user=current_user, setting_type=setting_type.value, category=category
    )
    update_settings = await dynamic_customization.build_main_setting_json(
        db=db, current_user=current_user
    )
    return update_settings


@router.get("/{user_id}/{study_area_id}", response_class=JSONResponse)
async def get_user_settings(
    *,
    db: AsyncSession = Depends(deps.get_db),
    study_area_id: int = None,
    user_id: int = None,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get customization settings for user.
    """
    customizations = await crud.customization.get_multi(db)
    settings = {}
    for customization in customizations:
        settings.update(customization.setting)
    user_customizations = await CRUDBase(models.UserCustomization).get_by_key(
        db, key="user_id", value=user_id
    )
    study_area = await CRUDBase(models.StudyArea).get(db, id=study_area_id)
    if study_area is not None and study_area.setting:
        settings.update(study_area.setting)

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
                study_area_id=study_area_id,
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
    if not customization:
        raise HTTPException(status_code=400, detail="Customization not found")
    else:
        customization = customization[0]

    user_customization = await CRUDBase(models.UserCustomization).get_by_multi_keys(
        db, keys={"user_id": user_id, "customization_id": customization.id}
    )

    if user_customization is not None and len(user_customization) > 0:
        await CRUDBase(models.UserCustomization).remove(db, id=user_customization[0].id)
    return {"msg": "Customization deleted"}


@router.get("/base", response_class=JSONResponse)
async def list_base_customizations(
    *,
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    ordering: str = None,
    q: str = None,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    settings = await crud.customization.get_multi(
        db, skip=skip, limit=limit, ordering=ordering, query=q
    )

    return settings


@router.get("/base/{id}", response_class=JSONResponse)
async def get_base_customization_by_id(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    customization = await crud.customization.get(db, id=id)
    if not customization:
        raise HTTPException(
            status_code=404,
            detail="Customization not found.",
        )

    return customization


@router.post("/base", response_class=JSONResponse)
async def create_base_customization(
    *,
    db: AsyncSession = Depends(deps.get_db),
    customization_in: models.CustomizationBase,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    customization = await crud.customization.create(db, obj_in=customization_in)
    return customization


@router.put("/base/{id}", response_class=JSONResponse)
async def update_base_customization(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    customization_in: models.CustomizationBase,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    customization = await crud.customization.get(db, id=id)
    if not customization:
        raise HTTPException(
            status_code=404,
            detail="Customization not found.",
        )
    customization = await crud.customization.update(
        db, db_obj=customization, obj_in=customization_in
    )
    return customization


@router.delete("/base/{id}", response_class=JSONResponse)
async def delete_base_customization(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    customization = await crud.customization.get(db, id=id)
    if not customization:
        raise HTTPException(
            status_code=404,
            detail="Customization not found.",
        )
    customization = await crud.customization.remove(db, id=id)
    return customization
