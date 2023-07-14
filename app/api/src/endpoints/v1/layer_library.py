from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud, schemas
from src.db import models
from src.endpoints.legacy import deps

router = APIRouter()


@router.get("", response_model=List[models.LayerLibrary])
async def list_layer_libraries(
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
async def read_layer_library_by_name(
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
async def create_a_new_layer_library(
    layer_in: schemas.CreateLayerLibrary,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    layer = await crud.layer_library.create(db, obj_in=layer_in)
    return layer


@router.put("/{name}", response_model=models.LayerLibrary)
async def update_a_layer_library(
    name: str,
    layer_in: schemas.CreateLayerLibrary,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    layer_in_db = await crud.layer_library.get_by_key(db, key="name", value=name)
    if not layer_in_db:
        raise HTTPException(status_code=404, detail="layer library not found.")

    layer = await crud.layer_library.update(db, db_obj=layer_in_db[0], obj_in=layer_in)
    return layer


@router.delete("/")
async def delete_layer_libraries(
    name: List[str] = Query(default=None),
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    return await crud.layer_library.remove_multi_by_key(db, key="name", values=name)


styles_router = APIRouter()


@styles_router.get("", response_model=List[models.StyleLibrary])
async def list_styles(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    styles = await crud.style_library.get_multi(db, skip=skip, limit=limit)
    if not styles:
        raise HTTPException(status_code=404, detail="there is no (more) style libraries.")
    return styles


@styles_router.get("/{name}", response_model=models.StyleLibrary)
async def read_style_by_name(
    name: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    style = await crud.style_library.get_by_key(db, key="name", value=name)
    if style:
        style = style[0]
    else:
        raise HTTPException(status_code=404, detail="style not found.")
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
    if not style_in_db:
        raise HTTPException(status_code=404, detail="style library not found.")
    style = await crud.style_library.update(db, db_obj=style_in_db[0], obj_in=style_in)
    return style


@styles_router.delete("/")
async def delete_style_libraries(
    name: List[str] = Query(default=None),
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    return await crud.style_library.remove_multi_by_key(db, key="name", values=name)
