from functools import lru_cache

from celery import Celery
from celery import current_app as current_celery_app

from core import file_manager
from settings import settings


def _set_autodiscover_tasks(celery_instance: Celery):
    app_paths = file_manager.get_application_paths()
    celery_instance.autodiscover_tasks(
        packages=[
            "core",
        ]
        + [f"apps.{app_path.stem}" for app_path in app_paths]
    )


def _update_conf(celery_instance: Celery):
    celery_instance.conf.update(
        broker_url=settings.celery_broker,
        result_backend=settings.celery_backend,
        task_concurrency=settings.celery_task_concurrency,
        worker_prefetch_multiplier=settings.celery_prefetch_multiplier,
        worker_heartbeat=settings.celery_worker_heartbeat,
        broker_connection_retry_on_startup=True,
        broker_connection_retry=True,
        enable_utc=True,
        timezone="UTC",
        task_default_queue="default",
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        beat_scheduler="redbeat.RedBeatScheduler",  # Use Redis for schedule storage
    )


def _scheduler_configs(celery_instance: Celery):
    celery_instance.conf.beat_schedule = {
        "print-message-every-10-seconds": {
            "task": "core.tasks.basic.print_message",
            "schedule": 10.0,  # Run every 10 seconds
        }
    }


@lru_cache
def main(p_main: str = __name__):
    celery = current_celery_app or Celery(p_main)
    _update_conf(celery)
    _set_autodiscover_tasks(celery)
    _scheduler_configs(celery)

    return celery
