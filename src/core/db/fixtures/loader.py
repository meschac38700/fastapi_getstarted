import asyncio
import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Literal

import settings
from core.db.fixtures import utils as fixture_utils
from core.db.fixtures.files import FixtureFileReader
from core.db.fixtures.model_loaders.factory import ModelLoaderFactory
from core.monitoring.logger import get_logger

_APP_DIR = settings.BASE_DIR / "apps"
_logger = get_logger(__name__)


class LoadFixtures:
    _ALLOWED_FILES = [".yaml", ".yml"]

    def __init__(
        self, app_dir: str | Path = _APP_DIR, *, logger: logging.Logger | None = None
    ):
        self.app_dir: Path = Path(app_dir)
        self.logger = logger or _logger
        self.count_created = 0
        self.model_loader = ModelLoaderFactory()
        self._loader_mapping = {
            "app": self.load_app_fixtures,
            "path": self.load_fixture_file,
            "name": self.load_fixture_by_name,
        }

    async def _load_models(self, file_path: Path) -> int:
        """Extract model instances from the given YAML file and load them."""
        fixture_file_reader = FixtureFileReader(file_path=file_path)
        data_list_groups = await fixture_file_reader.extract_data()
        created = 0
        for group_key, data_list in data_list_groups.items():
            count = len(data_list)
            await self.model_loader.load(data_list, group_key)
            self.logger.info(f"Loaded {count} objects of type {group_key}.")
            created += count
        return created

    async def load_fixture_file(self, fixture_file: Path | str):
        """Process and load the provided fixture files.

        example:
         > self.load_fixture_file("/src/apps/user/fixtures/users.yaml").
        """
        _fixture_file = Path(fixture_file).absolute()
        self.logger.info(f"Start processing file '{_fixture_file.name}'.")
        if not _fixture_file.exists():
            raise ValueError(
                f"Invalid fixture file: {_fixture_file}. File does not exists."
            )

        count_created = await self._load_models(_fixture_file)
        self.logger.info(
            f"{count_created} object(s) found in the {_fixture_file.name} file and will be saved in the database."
        )
        self.count_created += count_created

    async def load_app_fixtures(self, app_name: str):
        """Load all fixtures found in the provided app.

        example:
         > self.load_app_fixture('user')
        """
        self.logger.info(f"Start loading {app_name} fixtures.")
        fixture_files = fixture_utils.collect_app_fixtures(app_name)
        self.logger.info(
            f"{len(fixture_files)} fixture files found in the {app_name.title()} application."
        )
        tasks = [self.load_fixture_file(fixture_file) for fixture_file in fixture_files]
        await asyncio.gather(*tasks)
        self.logger.info(
            f"Loaded a total of {self.count_created} fixtures for the {app_name} application."
        )

    async def load_fixture_by_name(self, fixture_name: str) -> int:
        """Load ths given fixture name.

        example:
         > self.load_fixture_by_name(['initial_users'])
        """
        fixture_path = fixture_utils.retrieve_fixture_absolute_path(fixture_name)
        await self.load_fixture_file(fixture_path)

    async def load_fixtures(
        self,
        fixtures: Sequence[str | Path] | None = None,
        loader_key: Literal["app", "name", "path"] = "name",
    ):
        """Load application fixture data.

        If loader_key equals app, it will load all the app's fixtures; fixtures argument should contain a list of apps
        If loader_key equals name, it will search and load fixtures listed by name
        if loader_key equals a path, it will load the specified fixture paths if it exists
        """
        loader = self._loader_mapping.get(loader_key)
        if loader is None:
            raise ValueError(
                f"Invalid loader key '{loader_key}'. Expecting {tuple(self._loader_mapping.keys())}."
            )

        if fixtures is None:
            fixtures = settings.initial_fixtures

        for fixture in fixtures:
            await loader(fixture)
