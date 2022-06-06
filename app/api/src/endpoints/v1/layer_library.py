import http
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud, schemas
from src.db import models
from src.endpoints import deps

router = APIRouter()


@router.get("", response_model=List[models.LayerLibrary])
async def list_layers(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    layers = await crud.layer_library.get_multi(db, skip=skip, limit=limit)
    if not layers:
        raise HTTPException(status_code=404, detail="there is no (more) layer libraries.")
    return layers


@router.get("/{name}", response_model=models.LayerLibrary)
async def read_layer_by_name(
    name: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    layer = await crud.layer_library.get_by_key(db, key="name", value=name)
    if layer:
        layer = layer[0]
    else:
        raise HTTPException(status_code=404, detail="layer not found.")
    return layer


@router.post("", response_model=models.LayerLibrary)
async def create_layer(
    layer_in: schemas.CreateLayerLibrary,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    layer = await crud.layer_library.create(db, obj_in=layer_in)
    return layer


@router.put("/{name}", response_model=models.LayerLibrary)
async def update_layer(
    name: str,
    layer_in: schemas.CreateLayerLibrary,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    layer_in_db = await crud.layer_library.get_by_key(db, key="name", value=name)
    layer = await crud.layer_library.update(db, db_obj=layer_in_db[0], obj_in=layer_in)
    return layer


@router.delete("/{id}", response_model=models.LayerLibrary)
async def delete_layer(
    id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    layer = await crud.layer_library.remove(db, id=id)
    return layer
