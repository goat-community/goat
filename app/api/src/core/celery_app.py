from celery import Celery

from src.core.config import settings

celery_app = Celery("worker", broker=settings.CELERY_BROKER_URL, results_backend=settings.CELERY_RESULT_BACKEND, include=["src.endpoints.v1.data_preparation_tasks"])

celery_app.conf.task_routes = {"app.worker.test_celery": "main-queue"}
