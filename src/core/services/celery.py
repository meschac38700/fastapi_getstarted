from celery import Celery

from core import file_manager
from settings import settings


def celery_setup(celery: Celery):
    celery.conf.update(
        task_concurrency=settings.celery_task_concurrency,
        worker_prefetch_multiplier=settings.celery_prefetch_multiplier,
        worker_heartbeat=settings.celery_worker_heartbeat,
        broker_connection_retry=True,
        broker_connection_retry_on_startup=True,
        enable_utc=True,
        timezone="UTC",
    )
    app_paths = file_manager.get_application_paths()
    celery.autodiscover_tasks([f"apps.{app_path.stem}" for app_path in app_paths])
