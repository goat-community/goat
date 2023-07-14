from typing import Any

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import models
from src.db.models.legacy.config_validation import *
from src.endpoints.legacy import deps
from src.resources.enums import (
    AllowedVectorTables,
    ReturnType,
    SQLReturnTypes,
    StaticTableSQLActive,
)
from src.utils import return_geojson_or_geobuf

router = APIRouter()


@router.get("/active-study-area/{layer_name}")
async def get_static_vector_layer_intersected_by_study_area(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    layer_name: AllowedVectorTables,
    return_type: ReturnType,
):
    """Return features from selected layer intersecting the active study area in different geoformats"""
    _return_type = return_type.value
    if return_type == ReturnType.geobuf.value:
        _return_type = "db_geobuf"
    sql_query = text(
        SQLReturnTypes[_return_type].value % StaticTableSQLActive[layer_name.value].value
    )
    result = await db.execute(sql_query, {"study_area_id": current_user.active_study_area_id})

    return return_geojson_or_geobuf(result.fetchall()[0][0], _return_type)


@router.get("/all/{layer_name}", response_model=Any)
async def get_static_table_all_features(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
    layer_name: AllowedVectorTables,
):
    """Return all features from selected layer with some selected columns"""
    if layer_name.value == "sub_study_area":
        results = await db.execute(
            select(
                models.SubStudyArea.id,
                models.SubStudyArea.study_area_id,
                models.SubStudyArea.name,
                models.SubStudyArea.population,
            )
        )
    elif layer_name.value == "study_area":
        results = await db.execute(
            select(models.StudyArea.id, models.StudyArea.name, models.StudyArea.population)
        )

    results = results.fetchall()
    return jsonable_encoder(results)
