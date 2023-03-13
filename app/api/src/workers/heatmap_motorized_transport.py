import asyncio

from src.workers.celery_app import celery_app

from .method_connector import (
    create_traveltime_matrices_async,
)


@celery_app.task
def create_r5_traveltime_matrices_sync(current_super_user, parameters):
    loop = asyncio.get_event_loop()
    coroutine = create_traveltime_matrices_async(
        current_super_user=current_super_user, parameters=parameters
    )
    loop.run_until_complete(coroutine)
    return "Ok"
