from typing import List

import h3
from shapely import Polygon

from src.core.config import settings
from src.core.opportunity import Opportunity
from src.crud.crud_compute_heatmap import CRUDComputeHeatmap
from src.db import models
from src.db.session import legacy_engine
from src.schemas.data_preparation import (
    OpportunityMatrixParametersSingleBulk,
    TravelTimeMatrixParametersSingleBulk,
)
from src.schemas.isochrone import IsochroneMode


async def create_traveltime_matrices_async(current_super_user, parameters):
    current_super_user = models.User(**current_super_user)
    parameters = TravelTimeMatrixParametersSingleBulk(**parameters)
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


async def create_opportunity_matrices_async(user, parameters):
    user = models.User(**user)
    parameters = OpportunityMatrixParametersSingleBulk(**parameters)
    isochrone_dto = parameters.isochrone_dto
    opportunity_types = parameters.opportunity_types
    opportunities_modified_excluded = ["aoi"]
    opportnities_user_excluded = ["aoi", "population"]
    scenario_ids = parameters.scenario_ids
    user_data_ids = parameters.user_data_ids
    bulk_id = parameters.bulk_id
    crud_compute_heatmap = CRUDComputeHeatmap(current_user=user)
    bulk_geom = Polygon(h3.h3_to_geo_boundary(h=bulk_id, geo_json=True))
    opportunity = Opportunity()
    travel_time_matrices = await crud_compute_heatmap.read_travel_time_matrices(
        bulk_id=bulk_id, isochrone_dto=isochrone_dto, s3_folder=parameters.s3_folder
    )
    if travel_time_matrices is None:
        return "No travel time matrices found for bulk_id: {bulk_id}"
    # Compute base data
    if parameters.compute_base_data == True:
        for opportunity_type in opportunity_types:
            opportunities_base = opportunity.read_base_data(
                layer=opportunity_type, h3_indexes=[bulk_id], bbox_wkt=bulk_geom.wkt
            )
            if len(opportunities_base) == 0:
                continue
            await crud_compute_heatmap.compute_opportunity_matrix(
                bulk_id,
                isochrone_dto,
                opportunity_type,
                opportunities=opportunities_base,
                travel_time_matrices=travel_time_matrices
            )

    # Compute modified data
    for scenario_id in scenario_ids:
        for opportunity_type in set(opportunity_types) - set(opportunities_modified_excluded):
            opportunities_modified = opportunity.read_modified_data(
                db=legacy_engine,
                layer=opportunity_type,
                bbox_wkt=bulk_geom.wkt,
                scenario_id=scenario_id,
            )
            if len(opportunities_modified) == 0:
                continue
            await crud_compute_heatmap.compute_opportunity_matrix(
                bulk_id,
                isochrone_dto,
                opportunity_type,
                opportunities=opportunities_modified,
                travel_time_matrices=travel_time_matrices,
                output_path=f"{settings.CACHE_PATH}/user/scenario/{scenario_id}",
            )

    # Compute user data
    for user_data_id in user_data_ids:
        for opportunity_type in set(opportunity_types) - set(opportnities_user_excluded):
            opportunities_user = opportunity.read_user_data(
                db=legacy_engine,
                layer=opportunity_type,
                bbox_wkt=bulk_geom.wkt,
                user_data_id=user_data_id,
            )
            if len(opportunities_user) == 0:
                continue
            await crud_compute_heatmap.compute_opportunity_matrix(
                bulk_id,
                isochrone_dto,
                opportunity_type,
                opportunities=opportunities_user,
                travel_time_matrices=travel_time_matrices,
                output_path=f"{settings.CACHE_PATH}/user/data_upload/{user_data_id}",
            )
    return "Ok"


async def create_connectivity_matrices_async(current_super_user, parameters):
    crud_compute_heatmap = CRUDComputeHeatmap(current_user=current_super_user)
    await crud_compute_heatmap.compute_connectivity_matrix(**parameters)
