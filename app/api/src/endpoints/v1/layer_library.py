from typing import List

from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src.db import models
from src.endpoints import deps

router = APIRouter()


@router.get("")
async def read_layers(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    layers = await crud.layer_library.get_multi(db, skip=skip, limit=limit)
    return layers


@router.get("/{layer_name}", response_model=models.LayerLibrary)
async def read_layer_by_name(
    layer_name: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    layer = await crud.layer_library.get_by_key(db, key="name", value=layer_name)
    return layer


@router.post("", response_model=models.LayerLibrary)
async def create_layer(
    layer_in: models.LayerLibrary,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    layer = crud.layer_library.create(db, obj_in=layer_in)
    return layer
