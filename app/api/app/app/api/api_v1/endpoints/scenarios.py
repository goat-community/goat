from typing import Any

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse, StreamingResponse

from app import crud
from app.api import deps
from app.schemas.msg import Msg
from app.schemas.scenario import ScenarioBase, ScenarioImport

router = APIRouter()

# TODO: Get scenario layer names from config table
translation_layers = {
    "ways": "deleted_ways",
    "pois": "deleted_pois",
    "buildings": "deleted_buildings",
}


@router.post("/read-deleted-features", response_class=JSONResponse)
def read_deleted_features(
    *,
    db: Session = Depends(deps.get_db),
    scenario_in: ScenarioBase,
):
    """
    Reads deleted features from a scenario layer.
    """
    layer = translation_layers.get(layer_name)
    if not layer:
        raise HTTPException(status_code=404, detail=f"Layer {layer_name} not found.")

    features = crud.scenario.read_deleted_features(db=db, obj_in=scenario_in, layer=layer)
    return features


@router.post("/update-deleted-features", response_model=Msg)
def update_deleted_features(*, db: Session = Depends(deps.get_db), scenario_in: ScenarioBase):
    """
    Updates deleted features in a scenario layer.
    """
    layer = translation_layers.get(layer_name)
    if not layer:
        raise HTTPException(status_code=404, detail=f"Layer {layer_name} not found.")

    features = crud.scenario.update_deleted_features(db=db, obj_in=scenario_in)
    return features


@router.post("/delete-feature", response_model=Msg)
def delete_feature(
    *,
    db: Session = Depends(deps.get_db),
    scenario_in: ScenarioBase,
    feature_id: int,
):
    """
    Deletes a feature from a scenario layer.
    """
    layer = translation_layers.get(layer_name)
    if not layer:
        raise HTTPException(status_code=404, detail=f"Layer {layer_name} not found.")

    feature = crud.scenario.delete_feature(
        db=db, obj_in=scenario_in, feature_id=feature_id, layer=layer
    )
    return feature


@router.post("/{layer_name}/create", response_model=ScenarioBase)
@router.post("/{layer_name}/update", response_model=Msg)
@router.post("/{layer_name}/delete", response_model=Msg)
@router.post("/export", response_class=StreamingResponse)
def export_scenario(*, db: Session = Depends(deps.get_db), scenario_in: ScenarioBase) -> Any:
    """
    Export scenario.
    """
    scenario = crud.scenario.export_scenario(db=db, obj_in=scenario_in)
    return scenario


@router.post("/upload")
def upload_scenario(*, db: Session = Depends(deps.get_db), scenario_in: ScenarioBase) -> Any:
    """
    Upload scenario.
    """
    scenario = crud.scenario.upload_scenario(db=db, obj_in=scenario_in)
    return scenario


@router.post("/import")
def import_scenario(*, db: Session = Depends(deps.get_db), scenario_in: ScenarioImport) -> Any:
    """
    Import scenario.
    """
    scenario = crud.scenario.import_scenario(db=db, obj_in=scenario_in)
    return scenario


@router.post("/delete", response_model=Msg)
def delete_scenario(*, db: Session = Depends(deps.get_db), scenario_in: ScenarioBase) -> Any:
    """
    Delete scenario.
    """
    scenario = crud.scenario.delete_scenario(db=db, obj_in=scenario_in)
    return scenario
