import asyncio
import logging
from pathlib import Path

from core.services.celery import celery_app
from core.services.runners import FixtureRunner

_logger = logging.Logger(__file__)


@celery_app.task()
def task_load_fixtures(
    apps: list[str] | None = None,
    names: list[str] | None = None,
    paths: list[Path] | None = None,
) -> None:
    """Load project fixtures in celery."""

    runner = FixtureRunner(logger=_logger)
    asyncio.run(runner(app_names=apps, fixture_names=names, fixture_paths=paths))
