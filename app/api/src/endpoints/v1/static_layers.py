from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src.crud.crud_customization import customization, dynamic_customization
from src.db import models

from src.endpoints import deps
from src.db.models.config_validation import *
from fastapi.encoders import jsonable_encoder
from src.utils import return_geojson_or_geobuf

router = APIRouter()
    
@router.get("/static/{layer_name}") 
async def static_vector_layer(*, 
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User =  Depends(deps.get_current_active_user),
    layer_name: str, 
    return_type: str
):
    """Return selected layers in different vector formats"""
    layer_to_return = await crud.layer.static_vector_layer(db, current_user, layer_name, return_type)
    return return_geojson_or_geobuf(layer_to_return, return_type)