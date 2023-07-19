import json
import os
import shutil
import uuid
from tempfile import NamedTemporaryFile
from typing import IO, Any

from fastapi import APIRouter, Body, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from starlette import status

from src import crud, schemas
from src.crud.crud_customization import dynamic_customization
from src.db import models
from src.endpoints.legacy import deps
from src.resources.enums import MaxUploadFileSize
from src.schemas.upload import request_examples
from src.utils import delete_file

router = APIRouter()


@router.get("/poi")
async def get_custom_pois(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Get metadata for uploaded user data."""

    upload_objs = await crud.data_upload.get_by_multi_keys(
        db, keys={"user_id": current_user.id, "study_area_id": current_user.active_study_area_id}
    )

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
                "state": state,
                "reached_poi_heatmap_computed": obj.reached_poi_heatmap_computed,
            }

            response_objs.append(obj_dict)

    return json.loads(json.dumps(response_objs))


@router.post("/poi")
async def upload_custom_pois(
    *,
    db: AsyncSession = Depends(deps.get_db),
    file: UploadFile,
    poi_category=Body(..., example=request_examples["poi_category"]),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Handle uploaded custom pois."""
    defined_uuid = uuid.uuid4().hex
    file_name = defined_uuid + os.path.splitext(file.filename)[1]
    file_dir = f"/tmp/{file_name}"

    real_file_size = 0
    temp: IO = NamedTemporaryFile(delete=False)
    for chunk in file.file:
        real_file_size += len(chunk)
        if real_file_size > MaxUploadFileSize.max_upload_poi_file_size.value:
            temp.close()
            delete_file(temp.name)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="The uploaded file size is to big the largest allowd size is %s MB."
                % round(MaxUploadFileSize.max_upload_poi_file_size / 1024.0**2, 2),
            )

        temp.write(chunk)
    temp.close()

    # Write file to file system

    shutil.move(temp.name, file_dir)
    await crud.upload.upload_custom_pois(
        db=db,
        poi_category=poi_category,
        file=file,
        file_dir=file_dir,
        file_name=file_name,
        current_user=current_user,
    )

    updated_settings = await dynamic_customization.build_main_setting_json(
        db=db, current_user=current_user
    )

    return updated_settings


@router.delete("/poi/all")
async def delete_all_custom_pois(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
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
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Delete custom pois."""
    data_upload_obj = await crud.data_upload.get_by_multi_keys(
        db, keys={"id": data_upload_id, "user_id": current_user.id}
    )
    if data_upload_obj == []:
        raise HTTPException(status_code=400, detail="Data Upload not found.")

    await crud.upload.delete_custom_pois(
        db=db, data_upload_id=data_upload_id, current_user=current_user
    )
    return {"msg": "Successfully deleted custom pois"}


@router.patch("/poi")
async def set_active_state_of_custom_poi(
    *,
    db: AsyncSession = Depends(deps.get_db),
    custom_data_upload_state: schemas.CutomDataUploadState,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Set active state of a custom poi."""

    await crud.upload.set_active_state_of_custom_poi(
        db=db, current_user=current_user, obj_in=custom_data_upload_state
    )

    return {"msg": "Successfully updated active state of custom poi"}
