import logging

from core.monitoring.logger import get_logger
from core.services.celery import celery_app

_logger = get_logger(__name__, level=logging.DEBUG)


@celery_app.task()
def debug_task():
    _logger.debug("This is a periodic task running every 5 minutes.")
