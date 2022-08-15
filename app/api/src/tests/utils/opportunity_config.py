from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src.db import models
from src.schemas import CreateOpportunityStudyAreaConfig
from src.schemas.opportunity_config import request_examples


async def create_random_opportunity_config(
    db: AsyncSession,
) -> models.LayerLibrary:
    layer_library_in = request_examples.oportunity_study_area_config
    layer_library_in = CreateOpportunityStudyAreaConfig(**layer_library_in)
    layer = await crud.opportunity_study_area_config.create(db=db, obj_in=layer_library_in)
    return layer
