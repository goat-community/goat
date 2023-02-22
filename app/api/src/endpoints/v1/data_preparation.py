import json

from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.crud_compute_heatmap import CRUDComputeHeatmap
from src.db import models
from src.endpoints import deps
from src.schemas import data_preparation as schemas

from src.endpoints.v1 import data_preparation_connector, data_preparation_tasks

router = APIRouter()



@router.post("/travel-time-matrices")
async def get_bulk_ids_for_study_area(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_super_user: models.User = Depends(deps.get_current_active_superuser),
    parameters: schemas.BulkIdParameters = Body(..., example=schemas.BulkIdParametersExample)):
    
    crud_compute_heatmap = CRUDComputeHeatmap(db, current_super_user)
    return await crud_compute_heatmap.get_bulk_ids(**parameters.dict())

@router.post("/traveltime-matrices")
async def create_traveltime_matrices(
    *,
    current_super_user: models.User = Depends(deps.get_current_active_superuser),
    parameters: schemas.OpportunityMatrixParameters2 = Body(..., example=schemas.OpportunityMatrixParametersExample)):
    parameters = json.loads(parameters.json())
    parameters2 = parameters.copy()
    current_super_user = json.loads(current_super_user.json())
    for bulk_id in parameters["bulk_id"]:
        parameters2["bulk_id"] = bulk_id
        #await data_preparation_connector.create_traveltime_matrices_async(current_super_user, parameters2)
        data_preparation_tasks.create_traveltime_matrices_sync.delay(current_super_user, parameters2)
    return JSONResponse("Ok")

@router.post("/traveltime-matrices-debug")
async def create_traveltime_matrices(
    *,
    current_super_user: models.User = Depends(deps.get_current_active_superuser),
    parameters: schemas.OpportunityMatrixParameters2 = Body(..., example=schemas.OpportunityMatrixParametersExample)):
    parameters = json.loads(parameters.json())
    parameters2 = parameters.copy()
    current_super_user = json.loads(current_super_user.json())
    for bulk_id in parameters["bulk_id"]:
        parameters2["bulk_id"] = bulk_id
        await data_preparation_connector.create_traveltime_matrices_async(current_super_user, parameters2)
        #data_preparation_tasks.create_traveltime_matrices_sync.delay(current_super_user, parameters2)
    return JSONResponse("Ok")


@router.post("/opportunity-matrices")
async def create_opportunity_matrices(
    *,
    current_super_user: models.User = Depends(deps.get_current_active_superuser),
    parameters: schemas.OpportunityMatrixParameters2 = Body(..., example=schemas.OpportunityMatrixParametersExample)):
    parameters = json.loads(parameters.json())
    parameters2 = parameters.copy()
    current_super_user = json.loads(current_super_user.json())
    for bulk_id in parameters["bulk_id"]:
        parameters2["bulk_id"] = bulk_id
        # data_preparation_tasks.create_opportunity_matrices_sync.delay(current_super_user, parameters2)
        await data_preparation_connector.create_opportunity_matrices_async(current_super_user, parameters2)
    return JSONResponse("Ok")