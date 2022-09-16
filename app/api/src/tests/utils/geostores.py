from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src.db import models
from src.schemas.geostore import CreateGeostore, request_examples


async def create_sample_geostore(
    db: AsyncSession,
) -> models.LayerLibrary:
    geostore_in = request_examples.geostore
    geostore_in = CreateGeostore(**geostore_in)
    geostore = await crud.geostore.create(db=db, obj_in=geostore_in)
    return geostore


async def create_add_two_geostores_to_study_area(
    db: AsyncSession,
) -> int:
    geostore1 = await create_sample_geostore(db)
    geostore2 = await create_sample_geostore(db)
    first_study_area = await crud.study_area.get_first(db)
    await crud.study_area.add_geostore_to_study_area(db, first_study_area.id, geostore1.id)
    await crud.study_area.add_geostore_to_study_area(db, first_study_area.id, geostore2.id)
    return first_study_area.id


async def create_add_one_geostore_to_study_area(
    db: AsyncSession,
) -> Any:
    geostore1 = await create_sample_geostore(db)
    first_study_area = await crud.study_area.get_first(db)
    await crud.study_area.add_geostore_to_study_area(db, first_study_area.id, geostore1.id)
    return first_study_area.id, geostore1.id
