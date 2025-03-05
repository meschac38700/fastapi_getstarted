import glob
import logging
import re
from collections.abc import Iterable, Sequence
from importlib import import_module
from pathlib import Path
from typing import Any

import aiofiles
import yaml
from sqlmodel import SQLModel

import settings
from core.db import SQLTable

_APP_DIR = settings.BASE_DIR / "apps"
_logger = logging.getLogger(__name__)


class LoadFixtures:
    _ALLOWED_FILES = [".yaml", ".yml"]

    def __init__(
        self, app_dir: str | Path = _APP_DIR, *, logger: logging.Logger | None = None
    ):
        self.app_dir: Path = Path(app_dir)
        self.logger = logger or _logger
        self.count_created = 0

    def _fill_primary_key(self, model_data: dict[str, Any], data: dict[str, Any]):
        _data = data.copy()
        if (pk := model_data.get("id")) is not None:
            """
            There is a problem inserting data with primary key
            Work around by omitting the id field
            Open discussion: https://github.com/fastapi/sqlmodel/discussions/1267
            """
            self.logger.info(f"ID temporarily not supported: '{pk=}'.")
            _data["id"] = pk
        return _data

    def _get_model_data(self, model_str: str):
        """Return model module and model name."""
        pkg_name, _, model_name = model_str.partition(".")
        package_path = self.app_dir / pkg_name
        module_path = str(package_path / "models").replace(str(settings.BASE_DIR), "")
        module_import_path = re.sub("/", ".", module_path).strip(".")

        model_module = import_module(module_import_path)
        return model_module, model_name

    def _get_model_instance(self, model_data: dict[str, Any]):
        """Transform a dict to the correct model instance.
        Expected yaml structure:
            - model: hero.Hero
              id: 1
              properties:
                name: "Spider-Boy"
                secret_name: "Pedro Parqueador"
        """
        model_module, model_name = self._get_model_data(model_data["model"])
        kwargs: dict[str, Any] = model_data["properties"]
        kwargs = self._fill_primary_key(model_data, kwargs)

        model_class: type[SQLModel] = getattr(model_module, model_name)
        if model_class is None:
            raise ValueError(f"Model {model_name} not found in module: {model_module}.")

        return model_class(**kwargs)

    async def _yaml_to_models(self, file_path: Path) -> list[SQLModel]:
        models = []
        async with aiofiles.open(file_path, mode="r") as f:
            for model_data in yaml.safe_load(await f.read()):
                models.append(self._get_model_instance(model_data))
        return models

    async def _load_fixtures(self, fixture_files: Iterable[str]) -> int:
        count = 0
        for fixture_file in fixture_files:
            fixture_file_path = Path(fixture_file)

            models = await self._yaml_to_models(fixture_file_path)
            await SQLTable.objects().insert_batch(models)
            count += len(models)

        return count

    def _get_app_paths(self):
        """Scan apps dir to extract all application pathname."""
        return (
            potential_app
            for potential_app in glob.glob(str(self.app_dir / "*"))
            if (Path(potential_app) / "models").exists()
            or (Path(potential_app) / "models.py").exists()
        )

    def _order_by_desired_fixtures(
        self, app_paths: Iterable[str], fixture_names: Sequence[str]
    ):
        """Make a fixture path generator based on the order of the given fixture names.

        Allows fixtures to be loaded in the specified order.
        Thus, the developer defines the loading order of the fixtures.
        """
        paths = list(app_paths)
        for fixture_name in fixture_names:
            for path in paths:
                fixture_name = f"{Path(fixture_name).stem}.y*ml"
                fixtures_path = str(Path(path) / "**" / fixture_name)
                fixtures = glob.glob(fixtures_path, recursive=True)
                if fixtures:
                    yield path

    def _scan_fixture_files(self, app: Path):
        """Scan the given app path to extract all fixtures paths."""
        fixture_files = []
        for ext in self._ALLOWED_FILES:
            pattern = app / "fixtures" / "**" / f"*{ext}"
            fixture_files.extend(glob.glob(str(pattern), recursive=True))

        return fixture_files

    async def load_fixtures(self, fixture_names: Sequence[str] | None = None) -> int:
        _fixture_names = fixture_names or settings.initial_fixtures
        for app in self._order_by_desired_fixtures(
            self._get_app_paths(), _fixture_names
        ):
            _app = Path(app)
            fixtures_files = self._scan_fixture_files(_app)

            app_name = _app.stem.title()
            self.logger.info(f"Loading {app_name} fixtures.")
            count = await self._load_fixtures(
                self._filter_fixture_files(fixtures_files, _fixture_names)
            )
            self.logger.info(f"Loaded a total of {count} {app_name} elements.")
            self.count_created += count

        self.logger.info(f"Total of {self.count_created} fixtures loaded.")
        return self.count_created

    def _filter_fixture_files(
        self, fixture_files: Sequence[str], desired_fixture_names: Sequence[str]
    ) -> Iterable[str]:
        if not desired_fixture_names or not isinstance(desired_fixture_names, Iterable):
            desired_fixture_names = settings.initial_fixtures

        self.logger.info(f"Processing {len(desired_fixture_names)} fixture files.")
        return (
            fixture_file
            for fixture_file in fixture_files
            if Path(fixture_file).stem in desired_fixture_names
            or Path(fixture_file).name in desired_fixture_names
        )
