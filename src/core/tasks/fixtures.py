import asyncio
from pathlib import Path

from core.monitoring.logger import get_logger
from core.services.celery import celery_app
from core.services.runners import FixtureRunner

_logger = get_logger(__name__)


@celery_app.task()
def load_fixtures_task(
    apps: list[str] | None = None,
    names: list[str] | None = None,
    paths: list[Path] | None = None,
) -> None:
    """Load project fixtures in celery."""
    _logger.info(
        f"Task: Loading fixtures with args:\t\n{apps=},\t\n{names=},\t\n{paths=}"
    )
    runner = FixtureRunner(logger=_logger)
    asyncio.run(runner(app_names=apps, fixture_names=names, fixture_paths=paths))
    return runner.loader.count_created
