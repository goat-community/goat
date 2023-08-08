
import h3
from shapely import Polygon

from src.core.config import settings
from src.core.opportunity import Opportunity
from src.core.heatmap.heatmap_compute import ComputeHeatmap
from src.core.heatmap.heatmap_read import ReadHeatmap
from src.db import models
from src.db.session import legacy_engine
from src.schemas.data_preparation import (
    OpportunityMatrixParametersSingleBulk,
    TravelTimeMatrixParametersSingleBulk,
)
from src.schemas.heatmap import HeatmapSettings, HeatmapType, HeatmapConfigAggregatedData
from src.schemas.indicators import CalculateOevGueteklassenParameters
from src.schemas.isochrone import IsochroneMode
from src.crud.crud_indicator import indicator


async def create_traveltime_matrices_async(current_super_user, parameters):
    current_super_user = models.User(**current_super_user)
    parameters = TravelTimeMatrixParametersSingleBulk(**parameters)
    compute_heatmap = ComputeHeatmap(current_user=current_super_user)
    try:
        calculation_object = await compute_heatmap.create_calculation_object(
            isochrone_dto=parameters.isochrone_dto, bulk_id=parameters.bulk_id
        )
    except Exception as e:
        print(e)
        return "Could not create calculation object"
    mode = parameters.isochrone_dto.mode
    if mode == IsochroneMode.TRANSIT or mode == IsochroneMode.CAR:
        await compute_heatmap.compute_traveltime_motorized_transport(
            parameters.isochrone_dto,
            calculation_object,
            s3_folder=parameters.s3_folder,
        )
    else:
        await compute_heatmap.compute_traveltime_active_mobility(
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
    compute_heatmap = ComputeHeatmap(current_user=user)
    bulk_geom = Polygon(h3.h3_to_geo_boundary(h=bulk_id, geo_json=True))
    opportunity = Opportunity()
    travel_time_matrices = await compute_heatmap.read_travel_time_matrices(
        bulk_id=bulk_id, isochrone_dto=isochrone_dto, s3_folder=parameters.s3_folder
    )

    if travel_time_matrices is None:
        return "No travel time matrices found for bulk_id: {bulk_id}"
    # Compute base data
    if parameters.compute_base_data is True:
        for opportunity_type in opportunity_types:
            opportunity_type_read = opportunity_type
            if opportunity_type == "population":
                opportunity_type_read = "population_grouped"

            opportunities_base = opportunity.read_base_data(
                layer=opportunity_type_read,
                h3_indexes=[bulk_id],
                bbox_wkt=bulk_geom.wkt,
                s3_folder=parameters.s3_folder,
            )
            if len(opportunities_base) == 0:
                continue
            await compute_heatmap.compute_opportunity_matrix(
                bulk_id,
                isochrone_dto,
                opportunity_type,
                opportunities=opportunities_base,
                travel_time_matrices=travel_time_matrices,
                s3_folder=parameters.s3_folder,
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
            await compute_heatmap.compute_opportunity_matrix(
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
            await compute_heatmap.compute_opportunity_matrix(
                bulk_id,
                isochrone_dto,
                opportunity_type,
                opportunities=opportunities_user,
                travel_time_matrices=travel_time_matrices,
                output_path=f"{settings.CACHE_PATH}/user/data_upload/{user_data_id}",
            )
    return "Ok"


async def create_connectivity_matrices_async(current_super_user, parameters):
    compute_heatmap = ComputeHeatmap(current_user=current_super_user)
    await compute_heatmap.compute_connectivity_matrix(**parameters)


async def read_heatmap_async(current_user, heatmap_settings):
    current_user = models.User(**current_user)
    #heatmap_settings = HeatmapSettings(**settings)
    heatmap = ReadHeatmap(current_user=current_user)

    if heatmap_settings.heatmap_type == HeatmapType.modified_gaussian_population:
        """
        This is a special case where we need to call the modified gaussian calculation twice.
        The first time we calculate the modified gaussian and the second time we calculate the population.
        We then subtract the population from the modified gaussian to get the difference.
        todo: This should be refactored in the future to be more generic
        """
        # Modified gaussian calculation
        heatmap_settings.heatmap_type = HeatmapType.modified_gaussian
        modified_gausian_result = heatmap.read(heatmap_settings)

        # Population calculation
        heatmap_settings.heatmap_type = HeatmapType.aggregated_data
        heatmap_settings.heatmap_config = HeatmapConfigAggregatedData(**{"source": "population"})
        population_result = heatmap.read(heatmap_settings)

        difference_quantiles = (
            population_result["population_class"] - modified_gausian_result["agg_class"]
        ).round()

        result = {
            "h3_grid_ids": modified_gausian_result["h3_grid_ids"],
            "h3_polygons": modified_gausian_result["h3_polygons"],
            "agg_class": modified_gausian_result["agg_class"],
            "population_class": population_result["population_class"],
            "difference_class": difference_quantiles,
        }

    else:
        result = heatmap.read(heatmap_settings)
        # TODO: Find the best place where to round the results as this should be done at the very end
        # result["agg_class"] = result["agg_class"].round()

    # todo: Can be extended to other formats in the future based on return type
    geojson_result = heatmap.to_geojson(result, heatmap_settings)
    result = {
        "data": {
            "geojson": geojson_result,
        },
        "return_type": heatmap_settings.return_type.value,
        "hexlified": False,
        "data_source": "heatmap",
    }
    return result


async def read_pt_station_count_async(current_user, payload, return_type):
    current_user = models.User(**current_user)
    station_count_features = await indicator.count_pt_service_stations(**payload)
    return_data = {
        "data": {
            "geojson": station_count_features,
        },
        "return_type": return_type,
        "hexlified": False,
        "data_source": "pt_station_count",
    }
    return return_data


async def read_pt_oev_gueteklassen_async(current_user, payload, return_type):
    current_user = models.User(**current_user)
    payload = CalculateOevGueteklassenParameters(**payload)
    oev_gueteklassen_features = await indicator.compute_oev_gueteklassen(
        start_time=payload.start_time,
        end_time=payload.end_time,
        weekday=payload.weekday,
        study_area_ids=payload.study_area_ids,
        station_config=payload.station_config,
    )
    return_data = {
        "data": {
            "geojson": oev_gueteklassen_features,
        },
        "return_type": return_type,
        "hexlified": False,
        "data_source": "pt_oev_gueteklassen",
    }

    return return_data
