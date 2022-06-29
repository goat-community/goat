from typing import List

from fastapi import APIRouter, Depends
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
    current_user: models.User = Depends(deps.get_current_active_user),
):
    layers = await crud.layer_library.get_multi(db, skip=skip, limit=limit)
    return layers


@router.get("/{name}", response_model=models.LayerLibrary)
async def read_layer_by_name(
    name: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    layer = await crud.layer_library.get_by_key(db, key="name", value=name)
    layer = layer[0]
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


styles_router = APIRouter()


@styles_router.get("", response_model=List[models.StyleLibrary])
async def list_styles(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    styles = await crud.style_library.get_multi(db, skip=skip, limit=limit)
    return styles


@styles_router.get("/{name}", response_model=models.StyleLibrary)
async def read_style_by_name(
    name: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    style = await crud.style_library.get_by_key(db, key="name", value=name)
    style = style[0]
    return style


@styles_router.post("", response_model=models.StyleLibrary)
async def create_style(
    style_in: schemas.CreateStyleLibrary,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    style = await crud.style_library.create(db, obj_in=style_in)
    return style


@styles_router.put("/{name}", response_model=models.StyleLibrary)
async def update_style(
    name: str,
    style_in: schemas.CreateStyleLibrary,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    style_in_db = await crud.style_library.get_by_key(db, key="name", value=name)
    style = await crud.style_library.update(db, db_obj=style_in_db[0], obj_in=style_in)
    return style


@styles_router.delete("/{id}", response_model=models.StyleLibrary)
async def delete_style(
    id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    style = await crud.style_library.remove(db, id=id)
    return style
