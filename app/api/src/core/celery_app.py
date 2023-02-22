from celery import Celery

celery_app = Celery("worker", broker="redis://redis/0", results_backend="redis://redis/0", include=["src.endpoints.v1.data_preparation_tasks"])

celery_app.conf.task_routes = {"app.worker.test_celery": "main-queue"}
