from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from src import crud
from src.db import models
from src.db.models.config_validation import *
from src.endpoints import deps
from src.utils import return_geojson_or_geobuf
from src.crud.base import CRUDBase
from src.resources.enums import AllowedVectorTables, ReturnType, SQLReturnTypes, StaticTableSQLActive
from sqlalchemy import text, select  
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
    sql_query = text(SQLReturnTypes[return_type.value].value % StaticTableSQLActive[layer_name.value].value) 
    result = await db.execute(sql_query, {"study_area_id": current_user.active_study_area_id})

    return return_geojson_or_geobuf(result.fetchall()[0][0], return_type.value)


@router.get("/all/{layer_name}", response_model=Any)
async def get_static_table_all_features(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
    layer_name: AllowedVectorTables
):
    """Return all features from selected layer with some selected columns"""
    if layer_name.value == 'sub_study_area':
        results = await db.execute(select(models.SubStudyArea.id, models.SubStudyArea.study_area_id, models.SubStudyArea.name, models.SubStudyArea.population))
    elif layer_name.value == 'study_area':
        results = await db.execute(select(models.StudyArea.id, models.StudyArea.name, models.StudyArea.population))

    results = results.fetchall()
    return jsonable_encoder(results)
