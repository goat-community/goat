from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.endpoints import deps
from src.db import models
from typing import List
from src import crud

router = APIRouter()

@router.get("",response_model=List[models.LayerLibrary])
async def read_layers(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    layers = await crud.layer_library.get_multi(db, skip=skip, limit=limit)
    return layers

@router.get("/{layer_name}")
async def read_layer_by_name(
    layer_name: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    layer = await crud.layer_library.get_by_key(db,key="name", value=layer_name)
    return layer