from typing import Any

from fastapi import APIRouter, Body, Depends, File, UploadFile, HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession

from src import crud
from src.db import models
from src.endpoints import deps
from src.crud.crud_customization import dynamic_customization
from src.schemas.upload import request_examples
from src.db.models.config_validation import check_dict_schema, PoiCategory
import random

router = APIRouter()

@router.post("/poi/")
async def upload_custom_pois(*, 
    db: AsyncSession = Depends(deps.get_db),
    file: UploadFile, 
    poi_category = Body(..., example=request_examples["poi_category"]), 
    current_user: models.User = Depends(deps.get_current_active_user)
    ) -> Any:

    """Handle uploaded custom pois."""

    await crud.upload.upload_custom_pois(db=db,file=file, poi_category=poi_category, current_user=current_user)
        
    hex_color = "#%06x" % random.randint(0, 0xFFFFFF)
    new_setting = {poi_category:{"icon": "fas fa question", "color": [hex_color]}}

    if check_dict_schema(PoiCategory, new_setting) == False:
        raise HTTPException(status_code=400, detail="Invalid JSON-schema")

    await dynamic_customization.handle_user_setting_modification(db=db, current_user=current_user, setting_type='poi', changeset=new_setting, modification_type='insert')
    updated_settings = await dynamic_customization.build_main_setting_json(db=db, current_user=current_user)

    return updated_settings