from typing import Any

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse, StreamingResponse

from app import crud
from app.api import deps
from app.schemas.msg import Msg
from app.schemas.scenario import (
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
def create_scenario(*, db: Session = Depends(deps.get_db), scenario_in: ScenarioCreate):
    """
    Creates a scenario.
    """
    result = crud.scenario.create_scenario(db=db, obj_in=scenario_in)
    return result


@router.post("/update", response_model=Msg)
def update_scenario(*, db: Session = Depends(deps.get_db), scenario_in: ScenarioUpdate):
    """
    Updates a scenario.
    """

    result = crud.scenario.update_scenario(db=db, obj_in=scenario_in)
    return result


@router.post("/delete", response_model=Msg)
def delete_scenario(*, db: Session = Depends(deps.get_db), scenario_in: ScenarioDelete):
    """
    Deletes a scenario.
    """

    result = crud.scenario.delete_scenario(db=db, obj_in=scenario_in)
    return result


@router.post("/import")
def import_scenario(*, db: Session = Depends(deps.get_db), scenario_in: ScenarioImport) -> Any:
    """
    Import scenario.
    """
    result = crud.scenario.import_scenario(db=db, obj_in=scenario_in)
    return result


@router.post("/export", response_class=StreamingResponse)
def export_scenario(*, db: Session = Depends(deps.get_db), scenario_in: ScenarioBase) -> Any:
    """
    Export scenario.
    """
    result = crud.scenario.export_scenario(db=db, obj_in=scenario_in)
    return result


@router.post("/upload")
def upload_scenario(*, db: Session = Depends(deps.get_db), scenario_in: ScenarioBase) -> Any:
    """
    Upload scenario features.
    """
    result = crud.scenario.upload_scenario(db=db, obj_in=scenario_in)
    return result


@router.post("/delete-feature", response_model=Msg)
def delete_feature(*, db: Session = Depends(deps.get_db), scenario_in: ScenarioDelete):
    """
    Deletes a feature from a scenario layer.
    """

    result = crud.scenario.delete_feature(db=db, obj_in=scenario_in)
    return result


@router.post("/read-deleted-features", response_class=JSONResponse)
def read_deleted_features(
    *,
    db: Session = Depends(deps.get_db),
    scenario_in: ScenarioReadDeleted,
):
    """
    Reads deleted features from a scenario layer.
    """

    result = crud.scenario.read_deleted_features(db=db, obj_in=scenario_in)
    return result


@router.post("/update-deleted-features", response_model=Msg)
def update_deleted_features(
    *, db: Session = Depends(deps.get_db), scenario_in: ScenarioUpdateDeleted
):
    """
    Updates deleted features in a scenario layer.
    """

    result = crud.scenario.update_deleted_features(db=db, obj_in=scenario_in)
    return result


@router.post("/delete-all", response_model=Msg)
def update_deleted_features(*, db: Session = Depends(deps.get_db), scenario_in: ScenarioBase):
    """
    Delete all scenario data.
    """

    result = crud.scenario.delete_all_scenario(db=db, obj_in=scenario_in)
    return result
