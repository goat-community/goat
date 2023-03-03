from src.crud.crud_compute_heatmap import CRUDComputeHeatmap
from src.db import models
from src.schemas.data_preparation import (
    OpportunityMatrixParameters,
    OpportunityMatrixParametersSingleBulk,
)
from src.schemas.isochrone import IsochroneMode


async def create_traveltime_matrices_async(current_super_user, parameters):
    current_super_user = models.User(**current_super_user)
    parameters = OpportunityMatrixParametersSingleBulk(**parameters)
    crud_compute_heatmap = CRUDComputeHeatmap(current_user=current_super_user)
    calculation_object = await crud_compute_heatmap.create_calculation_object(
        isochrone_dto=parameters.isochrone_dto, bulk_id=parameters.bulk_id
    )
    mode = parameters.isochrone_dto.mode
    if mode == IsochroneMode.TRANSIT or mode == IsochroneMode.CAR:
        await crud_compute_heatmap.compute_traveltime_motorized_transport(
            parameters.isochrone_dto,
            calculation_object,
            s3_folder=parameters.s3_folder,
        )
    else:
        await crud_compute_heatmap.compute_traveltime_active_mobility(
            parameters.isochrone_dto,
            calculation_object,
            s3_folder=parameters.s3_folder,
        )

    return "Ok"


async def create_opportunity_matrices_async(current_super_user, parameters):
    current_super_user = models.User(**current_super_user)
    parameters = OpportunityMatrixParametersSingleBulk(**parameters)
    isochrone_dto = parameters.isochrone_dto
    buffer_size = (isochrone_dto.settings.speed / 3.6) * (isochrone_dto.settings.travel_time * 60)
    crud_compute_heatmap = CRUDComputeHeatmap(current_user=current_super_user)
    calculation_object = await crud_compute_heatmap.create_calculation_object(
        parameters.calculation_resolution, buffer_size, parameters.bulk_id
    )
    await crud_compute_heatmap.compute_opportunity_matrix(isochrone_dto, calculation_object)

    return "Ok"


async def create_connectivity_matrices_async(current_super_user, parameters):
    crud_compute_heatmap = CRUDComputeHeatmap(current_user=current_super_user)
    await crud_compute_heatmap.compute_connectivity_matrix(**parameters)
