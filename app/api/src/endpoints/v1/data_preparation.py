from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src import schemas
from src.crud.crud_compute_heatmap import CRUDComputeHeatmap
from src.db import models
from src.endpoints import deps

router = APIRouter()



@router.post("/travel-time-matrices")
async def get_bulk_ids_for_study_area(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_super_user: models.User = Depends(deps.get_current_active_superuser),
    parameters: schemas.BulkIdParameters = Body(..., example=schemas.BulkIdParametersExample)):
    
    crud_compute_heatmap = CRUDComputeHeatmap(db, current_super_user)
    return await crud_compute_heatmap.get_bulk_ids(**parameters.dict())

@router.post("/opportunity-matrices")
async def create_opportunity_matrices(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_super_user: models.User = Depends(deps.get_current_active_superuser),
    parameters: schemas.OpportunityMatrixParameters = Body(..., example=schemas.OpportunityMatrixParametersExample)):
    
    isochrone_dto = parameters.isochrone_dto
    buffer_size = isochrone_dto.settings.speed * (isochrone_dto.settings.travel_time * 60)
    crud_compute_heatmap = CRUDComputeHeatmap(db, current_super_user)
    calculation_object = await crud_compute_heatmap.create_calculation_object(parameters.calculation_resolution, buffer_size, parameters.bulk_id)
    await crud_compute_heatmap.compute_opportunity_matrix(isochrone_dto, calculation_object)
    return JSONResponse("Ok")

@router.post("/traveltime-matrices")
async def create_traveltime_matrices(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_super_user: models.User = Depends(deps.get_current_active_superuser),
    parameters: schemas.OpportunityMatrixParameters = Body(..., example=schemas.OpportunityMatrixParametersExample)):
    
    isochrone_dto = parameters.isochrone_dto
    buffer_size = isochrone_dto.settings.speed * (isochrone_dto.settings.travel_time * 60)
    crud_compute_heatmap = CRUDComputeHeatmap(db, current_super_user)
    calculation_object = await crud_compute_heatmap.create_calculation_object(parameters.calculation_resolution, buffer_size, parameters.bulk_id)
    await crud_compute_heatmap.compute_traveltime_active_mobility(isochrone_dto, calculation_object)
    return JSONResponse("Ok")