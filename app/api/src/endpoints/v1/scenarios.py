import asyncio
from typing import Any, List, Optional, Union

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio.session import AsyncSession

from src import crud, schemas
from src.db import models
from src.endpoints import deps
from src.resources.enums import ReturnWithoutDbGeobufEnum
from src.schemas.msg import Msg
from src.schemas.scenario import request_examples, scenario_deleted_columns
from src.utils import return_geojson_or_geobuf, to_feature_collection

router = APIRouter()

# --------------------------------Scenario Table---------------------------------------
# -------------------------------------------------------------------------------------


@router.post("", response_model=models.Scenario)
async def create_scenario(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    scenario_in: schemas.ScenarioCreate = Body(..., example=request_examples["create"]),
):
    """
    Create scenario.
    """
    cnt_scenario_user = await db.execute(
        select(func.count(models.Scenario.id)).where(models.Scenario.user_id == current_user.id)
    )
    cnt_scenario_user = cnt_scenario_user.fetchone()[0]
    if cnt_scenario_user >= current_user.limit_scenarios:
        raise HTTPException(
            status_code=400,
            detail="You reached the maximum number of %s scenarios."
            % current_user.limit_scenarios,
        )

    obj_scenario = models.Scenario(
        scenario_name=scenario_in.scenario_name,
        user_id=current_user.id,
        study_area_id=current_user.active_study_area_id,
    )
    result = await crud.scenario.create(db=db, obj_in=obj_scenario)
    return result


@router.get("", response_model=List[models.Scenario])
async def get_scenarios(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get all scenarios.
    """
    result = await crud.scenario.get_by_multi_keys(
        db=db,
        keys={"user_id": current_user.id, "study_area_id": current_user.active_study_area_id},
    )
    return result


@router.put("/{scenario_id}", response_model=models.Scenario)
async def update_scenario(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    scenario_id: int,
    scenario_in: schemas.ScenarioUpdate = Body(..., example=request_examples["update"]),
):
    """
    Update scenario.
    """
    scenario = await crud.scenario.get_by_multi_keys(
        db, keys={"id": scenario_id, "user_id": current_user.id}
    )
    if len(scenario) > 0:
        result = await crud.scenario.update(db=db, db_obj=scenario[0], obj_in=scenario_in)
        return result
    else:
        raise HTTPException(status_code=400, detail="Scenario not found")


@router.delete("/")
async def delete_scenario(
    *,
    id: List[int] = Query(default=None, gt=0),
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Delete scenario.
    """
    return await crud.scenario.remove_multi_by_id_and_userid(db, ids=id, user_id=current_user.id)


@router.get("/{scenario_id}/upload", response_model=Msg)
async def upload_scenario_changes(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    scenario_id: int,
):
    """
    Upload scenario changes.
    """
    scenario = await crud.scenario.get_by_multi_keys(
        db, keys={"id": scenario_id, "user_id": current_user.id}
    )
    if len(scenario) > 0:
        # TODO: Call network modification function
        await asyncio.sleep(5)
        return {"msg": "Scenario changes uploaded."}
    else:
        raise HTTPException(status_code=400, detail="Scenario not found")


# ------------------------Scenario Layers (_modified tables)---------------------------
# -------------------------------------------------------------------------------------


@router.get("/{scenario_id}/{layer_name}/features", response_class=JSONResponse)
async def read_scenario_features(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    scenario_id: int = Path(
        ..., description="Scenario ID", example=request_examples["read_features"]["scenario_id"]
    ),
    layer_name: schemas.ScenarioLayersNoPoisEnum = Path(
        ...,
        description="Scenario layer name to read",
        example=request_examples["read_features"]["layer_name"],
    ),
    intersect: Optional[str] = Query(
        default=None,
        description="WKT Geometry to intersect with layer. Geometry must be in EPSG:4326. If not specified, all features are returned (only for _modified tables).",
        example=request_examples["read_features"]["intersect"],
    ),
    return_type: ReturnWithoutDbGeobufEnum = Query(
        default=ReturnWithoutDbGeobufEnum.geojson, description="Return type of the response"
    ),
) -> Any:
    """
    Get features from scenario layers (default or modified).
    """
    scenario = await crud.scenario.get_by_multi_keys(
        db, keys={"id": scenario_id, "user_id": current_user.id}
    )
    if len(scenario) == 0:
        raise HTTPException(status_code=400, detail="Scenario not found")

    result = await crud.scenario.read_scenario_features(
        db, current_user, scenario_id, layer_name, intersect
    )
    features = to_feature_collection(
        result, exclude_properties=["coordinates_3857", "node_source", "node_target"]
    )
    if return_type.value == ReturnWithoutDbGeobufEnum.geojson.value:
        features = jsonable_encoder(features)

    return return_geojson_or_geobuf(features, return_type.value)


@router.delete("/{scenario_id}/{layer_name}/features-all", response_model=Msg)
async def delete_scenario_features(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    scenario_id: int = Path(
        ..., description="Scenario ID", example=request_examples["delete_feature"]["scenario_id"]
    ),
    layer_name: schemas.ScenarioLayerFeatureEnum = Path(
        ...,
        description="Scenario layer name to delete feature from",
        example=request_examples["delete_feature"]["layer_name"],
    ),
) -> Any:
    """
    Delete all features from scenario layers. This endpoint is used to delete features in "modified" tables.
    """
    scenario = await crud.scenario.get_by_multi_keys(
        db, keys={"id": scenario_id, "user_id": current_user.id}
    )
    if len(scenario) == 0:
        raise HTTPException(status_code=400, detail="Scenario not found")

    result = await crud.scenario.delete_scenario_features(
        db, current_user, scenario_id, layer_name
    )
    return result


@router.delete("/{scenario_id}/{layer_name}/features", response_model=Msg)
async def delete_selected_scenario_feature(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    scenario_id: int = Path(
        ..., description="Scenario ID", example=request_examples["delete_feature"]["scenario_id"]
    ),
    layer_name: schemas.ScenarioLayerFeatureEnum = Path(
        ...,
        description="Scenario layer name to delete feature from",
        example=request_examples["delete_feature"]["layer_name"],
    ),
    id: List[int] = Query(
        ...,
        description="Scenario feature ID to delete",
        example=request_examples["delete_feature"]["feature_id"],
    ),
):
    """
    Delete specific features from scenario layer. This endpoint is used to delete feature in "modified" tables.
    """
    scenario = await crud.scenario.get_by_multi_keys(
        db, keys={"id": scenario_id, "user_id": current_user.id}
    )
    if len(scenario) == 0:
        raise HTTPException(status_code=400, detail="Scenario not found")
    else:
        result = await crud.scenario.delete_scenario_feature(
            db, current_user, scenario_id, layer_name, id
        )
        return result


@router.post(
    "/{scenario_id}/{layer_name}/features",
    response_class=JSONResponse,
)
async def create_scenario_features(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    scenario_id: int = Path(
        ..., description="Scenario ID", example=request_examples["create_feature"]["scenario_id"]
    ),
    layer_name: schemas.ScenarioLayerFeatureEnum = Path(
        ...,
        description="Scenario layer name to create feature in",
        example=request_examples["create_feature"]["layer_name"],
    ),
    features_in: schemas.ScenarioFeatureCreate = Body(
        ...,
        examples=request_examples["create_feature"]["payload"],
    ),
):
    """
    Create feature in scenario layer. This endpoint is used to create features in "modified" tables.
    """
    scenario = await crud.scenario.get_by_multi_keys(
        db, keys={"id": scenario_id, "user_id": current_user.id}
    )
    if len(scenario) == 0:
        raise HTTPException(status_code=400, detail="Scenario not found")
    else:
        result = await crud.scenario.create_scenario_features(
            db, current_user, scenario_id, layer_name, features_in
        )
        features = to_feature_collection(
            result, exclude_properties=["coordinates_3857", "node_source", "node_target"]
        )
        return jsonable_encoder(features)


@router.put(
    "/{scenario_id}/{layer_name}/features",
    response_class=JSONResponse,
)
async def update_scenario_features(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    scenario_id: int = Path(
        ..., description="Scenario ID", example=request_examples["update_feature"]["scenario_id"]
    ),
    layer_name: schemas.ScenarioLayerFeatureEnum = Path(
        ...,
        description="Scenario layer name to update features in",
        example=request_examples["update_feature"]["layer_name"],
    ),
    features_in: schemas.ScenarioFeatureUpdate = Body(
        ...,
        examples=request_examples["update_feature"]["payload"],
    ),
):
    """
    Update feature in scenario layer. This endpoint is used to update features in "modified" tables.
    """
    scenario = await crud.scenario.get_by_multi_keys(
        db, keys={"id": scenario_id, "user_id": current_user.id}
    )
    if len(scenario) == 0:
        raise HTTPException(status_code=400, detail="Scenario not found")
    else:
        result = await crud.scenario.update_scenario_features(
            db, current_user, scenario_id, layer_name, features_in
        )
        features = to_feature_collection(
            result, exclude_properties=["coordinates_3857", "node_source", "node_target"]
        )
        return jsonable_encoder(features)


@router.get("/population_modification/{scenario_id}", response_class=JSONResponse)
async def population_modification(
    *,
    db: AsyncSession = Depends(deps.get_db),
    scenario_id: int = Path(
        ..., description="Scenario ID", example=request_examples["update_feature"]["scenario_id"]
    ),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    scenario_id = await deps.check_user_owns_scenario(
        db=db, current_user=current_user, scenario_id=scenario_id
    )
    await db.execute(
        text("SELECT * FROM basic.population_modification(:scenario_id);"),
        {"scenario_id": scenario_id},
    )
    await db.commit()
    return {"msg": "Successfully calculated population modification"}
