from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src.db import models
from src.endpoints.legacy import deps
from src.resources.enums import LayerGroupsEnum
from src.schemas.study_area import pydantify_config

router = APIRouter()


@router.get("/settings/{id}/{group_name}", response_model=List[str])
async def get_group_layers_of_study_area_setting(
    id: int,
    group_name: LayerGroupsEnum,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Update layers to specified layer-group settings in specified study-area.
    """
    study_area = await crud.study_area.get(db=db, id=id)
    if not study_area:
        raise HTTPException(status_code=404, detail="study area not found.")

    settings = pydantify_config(study_area.setting, validate=False)
    return getattr(settings, group_name)


@router.put("/settings/{id}/{group_name}", response_model=List[str])
async def update_group_layers_in_study_area_setting(
    id: int,
    group_name: LayerGroupsEnum,
    layers: List[str],
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Get layers under the specified layer-group of specified study-area
    """
    study_area = await crud.study_area.get(db=db, id=id)
    if not study_area:
        raise HTTPException(status_code=404, detail="study area not found.")

    setting = study_area.setting.copy()
    layer_groups = pydantify_config(setting, validate=False)  # Convert Settings to Pydantic
    setattr(layer_groups, group_name, layers)  # Set new settings
    listed_layer_groups = layer_groups.listify_config()  # Convert Back to list settings
    setting["layer_groups"] = listed_layer_groups
    study_area.setting = setting  # To trigger update

    new_study_area = await crud.study_area.update(db=db, db_obj=study_area, obj_in=study_area)
    try:
        new_setting = pydantify_config(new_study_area.setting)

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors())

    return getattr(new_setting, group_name)
