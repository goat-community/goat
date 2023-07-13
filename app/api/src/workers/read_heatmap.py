import asyncio

from src.workers.celery_app import celery_app
from src.workers.method_connector import (
    read_heatmap_async,
    read_pt_station_count_async,
    read_pt_oev_gueteklassen_async,
)
from src.core.config import settings


@celery_app.task(time_limit=settings.CELERY_TASK_TIME_LIMIT)
def read_heatmap_task(current_user, heatmap_settings):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    heatmap = loop.run_until_complete(read_heatmap_async(current_user, heatmap_settings))
    return heatmap


@celery_app.task(time_limit=settings.CELERY_TASK_TIME_LIMIT)
def read_pt_station_count_task(current_user, payload, return_type):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(
        read_pt_station_count_async(current_user, payload, return_type)
    )
    return result


@celery_app.task(time_limit=settings.CELERY_TASK_TIME_LIMIT)
def read_pt_oev_gueteklassen_task(current_user, payload, return_type):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(
        read_pt_oev_gueteklassen_async(current_user, payload, return_type)
    )
    return result
