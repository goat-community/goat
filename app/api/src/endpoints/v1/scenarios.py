import asyncio
from typing import Any, List, Optional, Union

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, StreamingResponse
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
    obj_scenario = models.Scenario(
        scenario_name=scenario_in.scenario_name,
        user_id=current_user.id,
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
    result = await crud.scenario.get_by_key(db=db, key="user_id", value=current_user.id)
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


@router.delete("/{scenario_id}", response_model=Msg)
async def delete_scenario(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    scenario_id: int,
):
    """
    Delete scenario.
    """
    scenario = await crud.scenario.get_by_multi_keys(
        db, keys={"id": scenario_id, "user_id": current_user.id}
    )
    if len(scenario) > 0:
        result = await crud.scenario.remove(db, id=scenario_id)
        return {"msg": "Scenario deleted."}
    else:
        raise HTTPException(status_code=400, detail="Scenario not found")


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


@router.get("/{scenario_id}/{layer_name}/deleted", response_model=List[Any])
async def read_scenario_deleted_feature_ids(
    *,
    db: AsyncSession = Depends(deps.get_db),
    scenario_id: int,
    layer_name: schemas.ScenarioLayersEnum,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get all deleted features.
    """
    scenario = await crud.scenario.get_by_multi_keys(
        db, keys={"id": scenario_id, "user_id": current_user.id}
    )
    if len(scenario) == 0:
        raise HTTPException(status_code=400, detail="Scenario not found")
    else:
        scenario = scenario[0]
        deleted_features_column = scenario_deleted_columns[layer_name.value]
        try:
            deleted_features = getattr(scenario, deleted_features_column)
            return deleted_features
        except:
            raise HTTPException(status_code=400, detail="Column not found")


@router.patch("/{scenario_id}/{layer_name}", response_model=models.Scenario)
async def update_scenario_deleted_feature_ids(
    *,
    db: AsyncSession = Depends(deps.get_db),
    scenario_id: int,
    layer_name: schemas.ScenarioLayersEnum,
    deleted_features_in: List[Union[int, str]] = Body(
        ..., example=request_examples["update_deleted_features"]
    ),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Update deleted features.
    """
    scenario = await crud.scenario.get_by_multi_keys(
        db, keys={"id": scenario_id, "user_id": current_user.id}
    )
    if len(scenario) == 0:
        raise HTTPException(status_code=400, detail="Scenario not found")
    else:
        scenario = scenario[0]
        deleted_features_column = scenario_deleted_columns[layer_name.value]
        if not hasattr(scenario, deleted_features_column):
            raise HTTPException(status_code=400, detail="Column not found")
        db_obj_in = {deleted_features_column: deleted_features_in}
        result = await crud.scenario.update(db=db, db_obj=scenario, obj_in=db_obj_in)
        return result


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


@router.delete("/{scenario_id}/{layer_name}/features", response_model=Msg)
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


@router.delete("/{scenario_id}/{layer_name}/features/{feature_id}", response_model=Msg)
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
    Delete specific features from scenario layer. This endpoint is used to delete feature in "modified" tables. For deleting
    features in "default" tables, use the "{PATCH}/scenarios" endpoint.
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


# -----------------------------------Export--------------------------------------------
# -------------------------------------------------------------------------------------


# # TODO: export scenario to zip file
# @router.get("/{scenario_id}/export", response_class=StreamingResponse)
# async def export_scenario(
#     *,
#     db: AsyncSession = Depends(deps.get_db),
#     current_user: models.User = Depends(deps.get_current_active_user),
#     scenario_id: int = Path(..., description="Scenario ID"),
# ):
#     """
#     Export scenario to zip file
#     """
#     scenario = await crud.scenario.get_by_multi_keys(
#         db, keys={"id": scenario_id, "user_id": current_user.id}
#     )
#     if len(scenario) == 0:
#         raise HTTPException(status_code=400, detail="Scenario not found")
#     else:
#         return await crud.scenario.export_scenario(db, current_user, scenario_id)
