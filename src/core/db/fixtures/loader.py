import glob
import re
from collections.abc import Iterable
from importlib import import_module
from pathlib import Path
from typing import Any

import aiofiles
import yaml
from sqlmodel import SQLModel

from core.db import SQLTable
from settings import BASE_DIR

_APP_DIR = BASE_DIR / "apps"


class LoadFixtures:
    _ALLOWED_FILES = [".yaml"]

    def __init__(self, app_dir: str | Path = _APP_DIR):
        self.app_dir: Path = Path(app_dir)
        self.count_created = 0

    def _get_model_data(self, model_str: str):
        """Return model module and model name."""
        pkg_name, _, model_name = model_str.partition(".")
        package_path = self.app_dir / pkg_name
        module_path = str(package_path / "models").replace(str(BASE_DIR), "")
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
        kwargs = model_data["properties"]
        if (pk := model_data.get("id")) is not None:
            kwargs["id"] = pk

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

    async def _load_fixtures(self, fixture_files: Iterable[str]):
        for fixture_file in fixture_files:
            fixture_file_path = Path(fixture_file)
            if fixture_file_path.suffix not in self._ALLOWED_FILES:
                continue

            models = await self._yaml_to_models(fixture_file_path)
            await SQLTable.objects().insert_batch(models)
            self.count_created += len(models)

    async def load_fixtures(
        self,
    ) -> int:
        for app in glob.glob(str(self.app_dir / "*")):
            fixture_folder = Path(app) / "fixtures"
            if not fixture_folder.is_dir():
                continue

            fixture_files = glob.glob(str(fixture_folder / "*"))
            await self._load_fixtures(fixture_files)

        return self.count_created
