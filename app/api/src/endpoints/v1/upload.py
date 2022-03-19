import json
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, UploadFile, Header
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from src.resources.enums import MaxUploadFileSize
from src import crud, schemas
from src.crud.crud_customization import dynamic_customization
from src.db import models
from src.endpoints import deps
from src.schemas.upload import request_examples
from typing import IO

from tempfile import NamedTemporaryFile
import shutil
from fastapi import Header, Depends, UploadFile, HTTPException
from starlette import status

router = APIRouter()


async def valid_content_length(content_length: int = Header(..., lt=MaxUploadFileSize.max_upload_poi_file_size)):
    return content_length

@router.get("/poi")
async def get_custom_pois(
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
            if obj.id in current_user.active_data_upload_ids:
                state = True
            else:
                state = False

            obj_dict = {
                "id": obj.id,
                "category": category[0][0],
                "upload_size": obj.upload_size,
                "creation_date": str(obj.creation_date),
                "state": state
            }

            response_objs.append(obj_dict)

    return json.loads(json.dumps(response_objs))

@router.post("/poi")
async def upload_custom_pois(
    *,
    db: AsyncSession = Depends(deps.get_db),
    file: UploadFile,
    poi_category=Body(..., example=request_examples["poi_category"]),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:

    """Handle uploaded custom pois."""

    real_file_size = 0
    for chunk in file.file:
        real_file_size += len(chunk)
        if real_file_size > MaxUploadFileSize.max_upload_poi_file_size.value:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, 
                detail="The uploaded file size is to big the largest allowd size is %s MB." % round(MaxUploadFileSize.max_upload_poi_file_size/1024.0**2,2)
            )

    await crud.upload.upload_custom_pois(
        db=db, file=file, poi_category=poi_category, current_user=current_user
    )

    updated_settings = await dynamic_customization.build_main_setting_json(
        db=db, current_user=current_user
    )

    return updated_settings


@router.delete("/poi/all")
async def delete_all_custom_pois(
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


@router.delete("/poi/{data_upload_id}")
async def delete_custom_pois(
    *,
    db: AsyncSession = Depends(deps.get_db),
    data_upload_id: int,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:

    """Delete custom pois."""

    await crud.upload.delete_custom_pois(
        db=db, data_upload_id=data_upload_id, current_user=current_user
    )
    return {"msg": "Successfully deleted custom pois"}


@router.patch("/poi")
async def set_active_state_of_custom_poi(
    *,
    db: AsyncSession = Depends(deps.get_db),
    custom_data_upload_state: schemas.CutomDataUploadState,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """Set active state of a custom poi."""

    await crud.upload.set_active_state_of_custom_poi(
        db=db, current_user=current_user, obj_in=custom_data_upload_state
    )

    return {"msg": "Successfully updated active state of custom poi"}
