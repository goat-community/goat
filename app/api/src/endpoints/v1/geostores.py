from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud, schemas
from src.db import models
from src.endpoints.legacy import deps

router = APIRouter()


@router.get("", response_model=List[models.Geostore])
async def list_geostores(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_super_user: models.User = Depends(deps.get_current_active_superuser),
):
    geostores = await crud.geostore.get_multi(db, skip=skip, limit=limit)
    if not geostores:
        raise HTTPException(status_code=404, detail="there is no (more) geostores.")
    return geostores


@router.get("/{id:int}", response_model=models.Geostore)
async def read_geostore_by_id(
    id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_super_user: models.User = Depends(deps.get_current_active_superuser),
):
    geostore = await crud.geostore.get(db, id=id)
    if not geostore:
        raise HTTPException(status_code=404, detail="geostore not found.")
    return geostore


@router.post("", response_model=models.Geostore)
async def create_a_new_geostore(
    geostore_in: schemas.CreateGeostore,
    db: AsyncSession = Depends(deps.get_db),
    current_super_user: models.User = Depends(deps.get_current_active_superuser),
):
    geostore = await crud.geostore.create(db, obj_in=geostore_in)
    return geostore


@router.put("/{id:int}", response_model=models.Geostore)
async def update_a_geostore(
    id: int,
    geostore_in: schemas.CreateGeostore,
    db: AsyncSession = Depends(deps.get_db),
    current_super_user: models.User = Depends(deps.get_current_active_superuser),
):
    geostore_in_db = await crud.geostore.get(db, id=id)
    if not geostore_in_db:
        raise HTTPException(status_code=404, detail="geostore not found.")

    geostore = await crud.geostore.update(db, db_obj=geostore_in_db, obj_in=geostore_in)
    return geostore


@router.delete("/")
async def delete_geostores(
    id: List[int] = Query(default=None, gt=0),
    db: AsyncSession = Depends(deps.get_db),
    current_super_user: models.User = Depends(deps.get_current_active_superuser),
):
    return await crud.geostore.remove_multi(db, ids=id)


@router.get("/study_area/{study_area_id:int}", response_model=List[models.Geostore])
async def list_study_area_geostores(
    study_area_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_super_user: models.User = Depends(deps.get_current_active_superuser),
):
    study_area = await crud.study_area.get(
        db, id=study_area_id, extra_fields=[models.StudyArea.geostores]
    )
    if not study_area:
        raise HTTPException(status_code=404, detail="study area not found.")

    geostores = study_area.geostores
    if not geostores:
        raise HTTPException(status_code=404, detail="this study area has no geostores.")
    return geostores


@router.post(
    "/study_area/{study_area_id:int}/add/{geostore_id:int}", response_model=List[models.Geostore]
)
async def add_geostore_to_study_area(
    study_area_id: int,
    geostore_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_super_user: models.User = Depends(deps.get_current_active_superuser),
):
    study_area = await crud.study_area.get(
        db, id=study_area_id, extra_fields=[models.StudyArea.geostores]
    )
    if not study_area:
        raise HTTPException(status_code=404, detail="study area not found.")

    geostore_in = await crud.geostore.get(db, id=geostore_id)
    if not geostore_in:
        raise HTTPException(status_code=404, detail="geostore not found.")

    geostores = study_area.geostores
    geostore_ids = [geostore.id for geostore in geostores]
    if geostore_in.id not in geostore_ids:
        await crud.study_area.add_geostore_to_study_area(db, study_area.id, geostore_in.id)
        geostores.append(geostore_in)

    return geostores


@router.delete(
    "/study_area/{study_area_id:int}/remove/{geostore_id:int}",
    response_model=List[models.Geostore],
)
async def delete_geostore_to_study_area(
    study_area_id: int,
    geostore_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_super_user: models.User = Depends(deps.get_current_active_superuser),
):
    study_area = await crud.study_area.get(
        db, id=study_area_id, extra_fields=[models.StudyArea.geostores]
    )
    if not study_area:
        raise HTTPException(status_code=404, detail="study area not found.")
    geostores = study_area.geostores
    geostores = [geo for geo in geostores if geo.id != geostore_id]
    study_area_geostore_relationships = await crud.study_area_geostore.get_by_multi_keys(
        db, keys={"study_area_id": study_area_id, "geostore_id": geostore_id}
    )

    for relationship in study_area_geostore_relationships:
        await crud.study_area_geostore.remove(db, id=relationship.id)

    return geostores
