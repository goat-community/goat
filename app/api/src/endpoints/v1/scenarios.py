from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse, StreamingResponse

from src import crud
from src.endpoints import deps
from src.schemas.msg import Msg
from src.schemas.scenario import (
    ScenarioBase,
    ScenarioCreate,
    ScenarioDelete,
    ScenarioImport,
    ScenarioReadDeleted,
    ScenarioUpdate,
    ScenarioUpdateDeleted,
)

router = APIRouter()


@router.post("/create", response_model=ScenarioBase)
async def create_scenario(*, db: AsyncSession = Depends(deps.get_db), scenario_in: ScenarioCreate):
    """
    Creates a scenario.
    """
    result = await crud.scenario.create_scenario(db=db, obj_in=scenario_in)
    return result


@router.post("/update", response_model=Msg)
async def update_scenario(*, db: AsyncSession = Depends(deps.get_db), scenario_in: ScenarioUpdate):
    """
    Updates a scenario.
    """

    result = await crud.scenario.update_scenario(db=db, obj_in=scenario_in)
    return result


@router.post("/delete", response_model=Msg)
async def delete_scenario(*, db: AsyncSession = Depends(deps.get_db), scenario_in: ScenarioDelete):
    """
    Deletes a scenario.
    """

    result = await crud.scenario.delete_scenario(db=db, obj_in=scenario_in)
    return result


@router.post("/import")
async def import_scenario(
    *, db: AsyncSession = Depends(deps.get_db), scenario_in: ScenarioImport
) -> Any:
    """
    Import scenario.
    """
    result = await crud.scenario.import_scenario(db=db, obj_in=scenario_in)
    return result


@router.post("/export", response_class=StreamingResponse)
async def export_scenario(
    *, db: AsyncSession = Depends(deps.get_db), scenario_in: ScenarioBase
) -> Any:
    """
    Export scenario.
    """
    result = await crud.scenario.export_scenario(db=db, obj_in=scenario_in)
    return result


@router.post("/upload")
async def upload_scenario(
    *, db: AsyncSession = Depends(deps.get_db), scenario_in: ScenarioBase
) -> Any:
    """
    Upload scenario features.
    """
    result = await crud.scenario.upload_scenario(db=db, obj_in=scenario_in)
    return result


@router.post("/delete-feature", response_model=Msg)
async def delete_feature(*, db: AsyncSession = Depends(deps.get_db), scenario_in: ScenarioDelete):
    """
    Deletes a feature from a scenario layer.
    """

    result = await crud.scenario.delete_feature(db=db, obj_in=scenario_in)
    return result


@router.post("/read-deleted-features", response_class=JSONResponse)
async def read_deleted_features(
    *,
    db: AsyncSession = Depends(deps.get_db),
    scenario_in: ScenarioReadDeleted,
):
    """
    Reads deleted features from a scenario layer.
    """

    result = await crud.scenario.read_deleted_features(db=db, obj_in=scenario_in)
    return result


@router.post("/update-deleted-features", response_model=Msg)
async def update_deleted_features(
    *, db: AsyncSession = Depends(deps.get_db), scenario_in: ScenarioUpdateDeleted
):
    """
    Updates deleted features in a scenario layer.
    """

    result = await crud.scenario.update_deleted_features(db=db, obj_in=scenario_in)
    return result


@router.post("/delete-all", response_model=Msg)
async def update_deleted_features(
    *, db: AsyncSession = Depends(deps.get_db), scenario_in: ScenarioBase
):
    """
    Delete all scenario data.
    """

    result = await crud.scenario.delete_all_scenario(db=db, obj_in=scenario_in)
    return result
