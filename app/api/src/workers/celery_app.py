from celery import Celery

from src.core.config import settings

celery_app = Celery("worker")
celery_app.conf.update(settings.CELERY_CONFIG)

celery_app.conf.task_routes = {
    "src.workers.heatmap_active_mobility.*": "goat-active-mobility-heatmap-worker",
    "src.workers.heatmap_motorized_transport.*": "goat-motorized-transport-heatmap-worker",
}


celery_app.config_from_object(settings.CELERY_CONFIG)
# celery_app.conf.task_always_eager=True
