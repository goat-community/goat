import asyncio

from src.core.celery_app import celery_app

from .data_preparation_connector import (
    create_connectivity_heatmaps_async,
    create_opportunity_matrices_async,
    create_traveltime_matrices_async,
)


@celery_app.task
def create_traveltime_matrices_sync(current_super_user, parameters):
    loop = asyncio.get_event_loop()
    coroutine = create_traveltime_matrices_async(current_super_user=current_super_user, parameters=parameters)
    loop.run_until_complete(coroutine)
    return "Ok"

@celery_app.task
def create_opportunity_matrices_sync(current_super_user, parameters):
    loop = asyncio.get_event_loop()
    coroutine = create_opportunity_matrices_async(current_super_user=current_super_user, parameters=parameters)
    loop.run_until_complete(coroutine)
    return "Ok"

@celery_app.task
def create_connectivity_heatmaps_sync(current_super_user, parameters):
    loop = asyncio.get_event_loop()
    coroutine = create_connectivity_heatmaps_async(current_super_user=current_super_user, parameters=parameters)
    loop.run_until_complete(coroutine)
    return "Ok"