from typing import Any, Dict

from fastapi import APIRouter, Body, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

from src import crud
from src.db import models
from src.endpoints import deps
from src.resources.enums import IsochroneExportType
from src.schemas.isochrone import (
    IsochroneDTO,
    IsochroneMultiCountPois,
    request_examples,
)

router = APIRouter()


@router.post("")
async def calculate_isochrone(
    *,
    db: AsyncSession = Depends(deps.get_db),
    isochrone_in: IsochroneDTO = Body(..., examples=request_examples["isochrone"]),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Calculate isochrone.
    """
    if isochrone_in.scenario.id:
        await deps.check_user_owns_scenario(db, isochrone_in.scenario.id, current_user)
    result = await crud.isochrone.calculate(db, isochrone_in, current_user)
    return result


# @router.get("/network/{isochrone_calculation_id}/{modus}", response_class=JSONResponse)
# async def calculate_reached_network(
#     *,
#     db: AsyncSession = Depends(deps.get_db),
#     current_user: models.User = Depends(deps.get_current_active_user),
#     isochrone_calculation_id: int = Path(..., description="Isochrone Calculation ID", example=1),
#     modus: CalculationTypes = Path(..., description="Calculation modus"),
#     return_type: ReturnType = Query(
#         description="Return type of the response", default=ReturnType.geojson
#     ),
# ) -> Any:
#     """
#     Calculate the reached network for a single isochrone.
#     """
#     await deps.check_user_owns_isochrone_calculation(
#         db=db, isochrone_calculation_id=isochrone_calculation_id, current_user=current_user
#     )

#     isochrone_calc_obj = await crud.isochrone_calculation.get_by_key(
#         db=db, key="id", value=isochrone_calculation_id
#     )
#     isochrone_calc_obj = isochrone_calc_obj[0]
#     isochrone_feature_obj = await crud.isochrone_feature.get_by_key(
#         db=db, key="isochrone_calculation_id", value=isochrone_calculation_id
#     )

#     minutes = int(max([obj.step for obj in isochrone_feature_obj]) / 60)

#     x, y = isochrone_calc_obj.starting_point.replace("POINT (", "").replace(")", "").split(" ")

#     obj_calculation = IsochroneSingle(
#         minutes=minutes,
#         speed=3.6 * isochrone_calc_obj.speed,
#         n=len(isochrone_feature_obj),
#         modus=modus.value,
#         x=x,
#         y=y,
#         user_id=current_user.id,
#         routing_profile=isochrone_calc_obj.routing_profile,
#         active_upload_ids=current_user.active_data_upload_ids,
#         scenario_id=isochrone_calc_obj.scenario_id,
#     )

#     network = await crud.isochrone.calculate_reached_network(db=db, obj_in=obj_calculation)

#     return return_geojson_or_geobuf(
#         json.JSONDecoder().decode(json.dumps(network)), return_type.value
#     )


# @router.post("/multi", response_class=JSONResponse)
# async def calculate_multi_isochrone(
#     *,
#     db: AsyncSession = Depends(deps.get_db),
#     isochrone_in: IsochroneMulti = Body(..., example=request_examples["multi_isochrone"]),
#     current_user: models.User = Depends(deps.get_current_active_user),
# ) -> Any:
#     """
#     Calculate multi isochrone.
#     """

#     isochrone_in.scenario_id = await deps.check_user_owns_scenario(
#         db=db, scenario_id=isochrone_in.scenario_id, current_user=current_user
#     )
#     isochrone_in.active_upload_ids = current_user.active_data_upload_ids
#     isochrone_in.user_id = current_user.id
#     isochrone = await crud.isochrone.calculate_multi_isochrones(db=db, obj_in=isochrone_in)
#     return json.loads(isochrone.to_json())


# @router.post("/multi/count-pois", response_class=JSONResponse)
# async def count_pois_multi_isochrones(
#     *,
#     db: AsyncSession = Depends(deps.get_db),
#     isochrone_in: IsochroneMultiCountPois = Body(
#         ..., examples=request_examples["pois_multi_isochrone_count_pois"]
#     ),
#     current_user: models.User = Depends(deps.get_current_active_user),
# ) -> Any:
#     """
#     Count pois under study area.
#     """
#     isochrone_in.scenario_id = await deps.check_user_owns_scenario(
#         db=db, scenario_id=isochrone_in.scenario_id, current_user=current_user
#     )
#     isochrone_in.active_upload_ids = current_user.active_data_upload_ids
#     isochrone_in.user_id = current_user.id
#     cnt = await crud.isochrone.count_pois_multi_isochrones(db=db, obj_in=isochrone_in)
#     return cnt


# @router.post("/multi/pois", response_class=JSONResponse)
# async def poi_multi_isochrones(
#     *,
#     db: AsyncSession = Depends(deps.get_db),
#     isochrone_in: IsochronePoiMulti = Body(
#         ..., examples=request_examples.get("pois_multi_isochrone_study_area")
#     ),
#     current_user: models.User = Depends(deps.get_current_active_user),
# ) -> Any:
#     """
#     Compute multiisochrone with POIs as starting points.
#     """
#     isochrone_in.scenario_id = await deps.check_user_owns_scenario(
#         db=db, scenario_id=isochrone_in.scenario_id, current_user=current_user
#     )
#     isochrone_in.active_upload_ids = current_user.active_data_upload_ids
#     isochrone_in.user_id = current_user.id
#     if (
#         isochrone_in.modus == CalculationTypes.default.value
#         or isochrone_in.modus == CalculationTypes.scenario.value
#     ):
#         gdf = await crud.isochrone.calculate_pois_multi_isochrones(
#             db=db, current_user=current_user, obj_in=isochrone_in
#         )
#     elif isochrone_in.modus == CalculationTypes.comparison.value:
#         isochrone_in.modus = CalculationTypes.default.value
#         gdf_default = await crud.isochrone.calculate_pois_multi_isochrones(
#             db=db, current_user=current_user, obj_in=isochrone_in
#         )
#         isochrone_in.modus = CalculationTypes.scenario.value
#         gdf_scenario = await crud.isochrone.calculate_pois_multi_isochrones(
#             db=db, current_user=current_user, obj_in=isochrone_in
#         )

#         gdf = GeoDataFrame(pd.concat([gdf_default, gdf_scenario]))

#     return json.loads(gdf.reset_index(drop=True).to_json())


@router.post("/multi/count-pois", response_class=JSONResponse)
async def count_pois_multi_isochrones(
    *,
    db: AsyncSession = Depends(deps.get_db),
    isochrone_in: IsochroneMultiCountPois = Body(
        ..., examples=request_examples["pois_multi_isochrone_count_pois"]
    ),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Count pois under study area.
    """
    isochrone_in.scenario_id = await deps.check_user_owns_scenario(
        db=db, scenario_id=isochrone_in.scenario_id, current_user=current_user
    )
    isochrone_in.active_upload_ids = current_user.active_data_upload_ids
    isochrone_in.user_id = current_user.id
    cnt = await crud.isochrone.count_opportunity(db=db, obj_in=isochrone_in)
    return cnt


@router.post("/export", response_class=StreamingResponse)
async def export_isochrones(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    geojson: Dict = Body(..., examples=request_examples["to_export"]),
    return_type: IsochroneExportType = Query(
        description="Return type of the response", default=IsochroneExportType.geojson
    ),
) -> Any:
    """
    Export isochrones from GeoJSON data.
    """

    file_response = await crud.isochrone.export_isochrone(
        db=db,
        current_user=current_user,
        return_type=return_type.value,
        geojson_dictionary=geojson,
    )
    return file_response
