from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src.db import models
from src.schemas import CreateLayerLibrary
from src.schemas.layer_library import request_examples


async def create_random_layer_library(
    db: AsyncSession,
    layer_library_in: CreateLayerLibrary = request_examples["single_layer_library"](),
) -> models.LayerLibrary:
    layer = await crud.layer_library.create(db=db, obj_in=layer_library_in)
    return layer
