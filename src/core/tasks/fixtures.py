import asyncio
import logging
from pathlib import Path

from core.services.celery import celery_app
from core.services.runners import FixtureRunner

_logger = logging.Logger(__file__)


@celery_app.task()
def task_load_fixtures(apps: list[str], names: list[str], paths: list[Path]) -> None:
    """Load project fixtures in celery."""

    runner = FixtureRunner(logger=_logger)
    asyncio.run(runner(app_names=apps, fixture_names=names, fixture_paths=paths))
