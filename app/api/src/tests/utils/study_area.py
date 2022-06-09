from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src.db.models import StudyArea

from .utils import random_lower_string


async def duplicate_first_study_area(db: AsyncSession) -> StudyArea:
    """
    Duplicate to maipulate by test
    """
    first_study_area = await crud.study_area.get_first(db=db)
    # del first_study_area.id
    # TODO: get next id? or convert to dictionary?
    # To convert to dictionary we need to determine the type of geo fields.
    first_study_area.name = random_lower_string()
    first_study_area = jsonable_encoder(first_study_area)

    duplicated_study_area = await crud.study_area.create(obj_in=first_study_area, db=db)
    return duplicated_study_area
