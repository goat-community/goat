import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src.crud.base import CRUDBase
from src.db import models
from src.endpoints import deps
from src.resources.enums import ReturnWithoutDbGeobufEnum
from src.utils import return_geojson_or_geobuf

router = APIRouter()

# ----------------------INDICATORS ENDPOINTS------------------------
# ------------------------------------------------------------------


@router.get("/indicators/stations-count")
async def count_pt_service_stations(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    start_time: Optional[int] = Query(
        description="Start time in seconds since midnight (Default: 07:00)",
        default=25200,
        ge=0,
        le=86400,
    ),
    end_time: Optional[int] = Query(
        description="End time in seconds since midnight (Default: 09:00)",
        default=32400,
        ge=0,
        le=86400,
    ),
    weekday: Optional[int] = Query(
        description="Weekday (1 = Monday, 7 = Sunday) (Default: Monday)", default=1, ge=1, le=7
    ),
    study_area_id: Optional[int] = Query(
        default=None, description="Study area id (Default: User active study area)"
    ),
    return_type: ReturnWithoutDbGeobufEnum = Query(
        default=ReturnWithoutDbGeobufEnum.geojson, description="Return type of the response"
    ),
):
    """
    Return the number of trips for every route type on every station given a time period and weekday.
    """
    if start_time >= end_time:
        raise HTTPException(status_code=422, detail="Start time must be before end time")

    is_superuser = crud.user.is_superuser(current_user)
    if study_area_id is not None and not is_superuser:
        owns_study_area = await CRUDBase(models.UserStudyArea).get_by_multi_keys(
            db, keys={"user_id": current_user.id, "study_area_id": study_area_id}
        )
        if owns_study_area == []:
            raise HTTPException(
                status_code=400,
                detail="The user doesn't own the study area or user doesn't have enough privileges",
            )
    else:
        study_area_id = study_area_id or current_user.active_study_area_id

    stations_count = await crud.public_transport.count_pt_service_stations(
        db=db,
        start_time=start_time,
        end_time=end_time,
        weekday=weekday,
        study_area_id=study_area_id,
        return_type=return_type,
    )
    return return_geojson_or_geobuf(stations_count, return_type.value)


@router.get("/indicators/oev-gueteklassen")
async def calculate_oev_gueteklassen(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    start_time: Optional[int] = Query(
        description="Start time in seconds since midnight (Default: 07:00)",
        default=25200,
        ge=0,
        le=86400,
    ),
    end_time: Optional[int] = Query(
        description="End time in seconds since midnight (Default: 09:00)",
        default=32400,
        ge=0,
        le=86400,
    ),
    weekday: Optional[int] = Query(
        description="Weekday (1 = Monday, 7 = Sunday) (Default: Monday)", default=1, ge=1, le=7
    ),
    study_area_id: Optional[int] = Query(
        default=None, description="Study area id (Default: User active study area)"
    ),
    return_type: ReturnWithoutDbGeobufEnum = Query(
        default=ReturnWithoutDbGeobufEnum.geojson, description="Return type of the response"
    ),
):
    """
    ÖV-Güteklassen (The public transport quality classes) is an indicator for access to public transport.
    The indicator makes it possible to identify locations which, thanks to their good access to public transport, have great potential as focal points for development.
    The calculation in an automated process from the data in the electronic timetable (GTFS).
    """
    if start_time >= end_time:
        raise HTTPException(status_code=422, detail="Start time must be before end time")

    is_superuser = crud.user.is_superuser(current_user)
    if study_area_id is not None and not is_superuser:
        owns_study_area = await CRUDBase(models.UserStudyArea).get_by_multi_keys(
            db, keys={"user_id": current_user.id, "study_area_id": study_area_id}
        )
        if owns_study_area == []:
            raise HTTPException(
                status_code=400,
                detail="The user doesn't own the study area or user doesn't have enough privileges",
            )
    else:
        study_area_id = study_area_id or current_user.active_study_area_id

    oev_gueteklassen_features = await crud.public_transport.compute_oev_gueteklassen(
        db=db,
        start_time=start_time,
        end_time=end_time,
        weekday=weekday,
        study_area_id=study_area_id,
    )
    if return_type.value == ReturnWithoutDbGeobufEnum.geojson.value:
        oev_gueteklassen_features = jsonable_encoder(oev_gueteklassen_features)
    return return_geojson_or_geobuf(oev_gueteklassen_features, return_type.value)


@router.get("/indicators/ptal")
async def calculate_ptal(
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    PTAL
    """
    return ""
