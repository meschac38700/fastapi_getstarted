import logging
from pathlib import Path
from typing import Literal

import settings
from core.db.fixtures import LoadFixtures
from core.monitoring.logger import get_logger

_logger = get_logger(__name__)


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
        loader_key: Literal["name", "path", "app"] = "name"
        fixtures = fixture_paths or settings.initial_fixtures

        if fixture_paths:
            loader_key = "path"
            fixtures = fixture_paths

        if app_names:
            loader_key = "app"
            fixtures = app_names

        await self.loader.load_fixtures(fixtures, loader_key)

        self.logger.info(
            f"Total of {self.loader.count_created} fixtures loaded successfully."
        )
