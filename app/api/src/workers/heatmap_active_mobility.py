import asyncio

from src.workers.celery_app import celery_app

from src.workers.method_connector import (
    create_connectivity_matrices_async,
    create_opportunity_matrices_async,
    create_traveltime_matrices_async,
)


@celery_app.task
def create_traveltime_matrices_sync(current_super_user, parameters):
    loop = asyncio.get_event_loop()
    coroutine = create_traveltime_matrices_async(current_super_user, parameters)
    loop.run_until_complete(coroutine)
    return "Ok"

@celery_app.task
def create_opportunity_matrices_sync(current_super_user, parameters):
    loop = asyncio.get_event_loop()
    coroutine = create_opportunity_matrices_async(current_super_user, parameters)
    loop.run_until_complete(coroutine)
    return "Ok"

@celery_app.task
def create_connectivity_matrices_sync(current_super_user, parameters):
    loop = asyncio.get_event_loop()
    coroutine = create_connectivity_matrices_async(current_super_user, parameters)
    loop.run_until_complete(coroutine)
    return "Ok"
