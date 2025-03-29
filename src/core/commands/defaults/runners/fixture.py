import logging
from pathlib import Path

from sqlalchemy.exc import IntegrityError

import settings
from core.db.fixtures import LoadFixtures

_logger = logging.getLogger(__name__)


class FixtureRunner:
    def __init__(self, *, logger: logging.Logger | None = None):
        self.logger = logger or _logger
        self.loader = LoadFixtures(logger=self.logger)

    async def __call__(
        self,
        *,
        app_names: list[str] | None = None,
        fixture_paths: list[Path] | None = None,
        fixture_names: list[str] | None = None,
    ):
        """Load application fixtures."""
        try:
            if fixture_paths:
                await self.loader.load_fixtures(fixture_paths, "path")

            if app_names:
                await self.loader.load_fixtures(app_names, "app")

            await self.loader.load_fixtures(fixture_paths or settings.initial_fixtures)

        except IntegrityError:
            self.logger.info(
                "It looks like loading fixtures might cause data integrity issues."
            )
            return
        self.logger.info("All fixtures loaded successfully.")
