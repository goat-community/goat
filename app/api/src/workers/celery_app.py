from celery import Celery

from src.core.config import settings

celery_app = Celery(
    "worker",
    include=["src.workers.heatmap_active_mobility", "src.workers.heatmap_motorized_transport", "src.workers.read_heatmap", "src.workers.isochrone"],
    task_create_missing_queues=True,
)
celery_app.conf.update(settings.CELERY_CONFIG)

celery_app.conf.update(
    task_routes={
        "src.workers.heatmap_active_mobility.*": {"queue": "goat-heavy-worker"},
        "src.workers.heatmap_motorized_transport.*": {
            "queue": "goat-superheavy-worker"
        },
        "src.workers.read_heatmap.*": {"queue": "goat-light-worker"},
        "src.workers.isochrone.*": {"queue": "goat-light-worker"},
    }
)


# celery -A src.workers.celery_app worker -l info -c 1 -Q goat-light-worker
