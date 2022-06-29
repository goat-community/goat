from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src.db import models
from src.schemas import CreateLayerLibrary, CreateStyleLibrary
from src.schemas.layer_library import request_examples


async def create_random_layer_library(
    db: AsyncSession,
) -> models.LayerLibrary:
    layer_library_in = request_examples.single_layer_library
    layer_library_in = CreateLayerLibrary(**layer_library_in)
    layer = await crud.layer_library.create(db=db, obj_in=layer_library_in)
    return layer


async def create_random_style_library(
    db: AsyncSession,
) -> models.StyleLibrary:
    style_library_in = request_examples.single_style_library
    style_library_in = CreateStyleLibrary(**style_library_in)
    style = await crud.style_library.create(db=db, obj_in=style_library_in)
    return style
