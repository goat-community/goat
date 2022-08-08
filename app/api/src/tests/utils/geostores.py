from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src.db import models
from src.schemas.geostore import CreateGeostore, request_examples


async def create_sample_geostore(
    db: AsyncSession,
) -> models.LayerLibrary:
    geostore_in = request_examples["geostore"]
    geostore_in = CreateGeostore(**geostore_in)
    geostore = await crud.geostore.create(db=db, obj_in=geostore_in)
    return geostore
