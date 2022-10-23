from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src.db import models
from src.schemas import CreateOpportunityStudyAreaConfig
from src.schemas.opportunity_config import request_examples


async def create_random_opportunity_config(
    db: AsyncSession,
) -> models.LayerLibrary:
    opportunity_config_in = await request_examples.async_oportunity_study_area_config(db=db)
    opportunity_config_in = CreateOpportunityStudyAreaConfig(**opportunity_config_in)
    layer = await crud.opportunity_study_area_config.create(db=db, obj_in=opportunity_config_in)
    return layer
