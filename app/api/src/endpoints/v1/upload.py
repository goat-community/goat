import json
import random
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from starlette.responses import JSONResponse

from src import crud
from src.crud.crud_customization import dynamic_customization
from src.db import models
from src.db.models.config_validation import PoiCategory, check_dict_schema
from src.endpoints import deps
from src.schemas.upload import request_examples

router = APIRouter()


@router.get("/metadata")
async def upload_custom_pois(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """Get metadata for uploaded user data."""

    upload_objs = await crud.data_upload.get_by_key(db, key="user_id", value=current_user.id)

    response_objs = []
    for obj in upload_objs:
        category = await db.execute(
            select(models.PoiUser.category).where(models.PoiUser.data_upload_id == obj.id).limit(1)
        )
        category = category.all()
        if category != []:
            obj_dict = {
                "category": category[0][0],
                "upload_size": obj.upload_size,
                "creation_data": str(obj.creation_date),
            }

            response_objs.append(obj_dict)

    return json.loads(json.dumps(response_objs))


@router.post("/upload/poi")
async def upload_custom_pois(
    *,
    db: AsyncSession = Depends(deps.get_db),
    file: UploadFile,
    poi_category=Body(..., example=request_examples["poi_category"]),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:

    """Handle uploaded custom pois."""

    await crud.upload.upload_custom_pois(
        db=db, file=file, poi_category=poi_category, current_user=current_user
    )

    hex_color = "#%06x" % random.randint(0, 0xFFFFFF)
    new_setting = {poi_category: {"icon": "fas fa question", "color": [hex_color]}}

    if check_dict_schema(PoiCategory, new_setting) == False:
        raise HTTPException(status_code=400, detail="Invalid JSON-schema")

    await dynamic_customization.handle_user_setting_modification(
        db=db,
        current_user=current_user,
        setting_type="poi",
        changeset=new_setting,
        modification_type="insert",
    )
    updated_settings = await dynamic_customization.build_main_setting_json(
        db=db, current_user=current_user
    )

    return updated_settings

@router.post("/delete/poi/")
async def delete_custom_pois(
    *,
    db: AsyncSession = Depends(deps.get_db),
    data_upload_id: int = Body(..., example=request_examples["delete_upload"]),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:

    """Delete custom pois."""

    await crud.upload.delete_custom_pois(
        db=db, data_upload_id=data_upload_id, current_user=current_user
    )
    return {"msg": "Successfully deleted custom pois"}


@router.get("/delete/poi/all")
async def delete_custom_pois(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:

    """Delete custom pois."""
    data_upload_ids = await crud.data_upload.get_by_key(db, key="user_id", value=current_user.id)

    for obj in data_upload_ids:
        await crud.upload.delete_custom_pois(
            db=db, data_upload_id=obj.id, current_user=current_user
        )

    return {"msg": "Successfully deleted custom pois"}