import logging
from importlib import import_module
from types import ModuleType
from typing import Any

import settings
from core.db.fixtures.files import ModelDataType
from core.monitoring.logger import get_logger
from core.services import files as file_services

_logger = get_logger(__name__)


class ModelBaseLoader[T]:
    def __init__(self, p_logger: logging.Logger | None = None):
        self.app_dir = settings.BASE_DIR / "apps"
        self.logger = p_logger or _logger

    def _fill_primary_key(self, model_data: ModelDataType, properties: dict[str, Any]):
        _properties = properties.copy()
        if (pk := model_data.get("id")) is not None:
            """
            There is a problem inserting data with primary key
            Work around by omitting the id field
            Open discussion: https://github.com/fastapi/sqlmodel/discussions/1267
            """
            self.logger.info(f"ID temporarily not supported: '{pk=}'.")
            _properties["id"] = pk
        return _properties

    def _module_and_class(self, model_str: str) -> tuple[ModuleType, type[T]]:
        """Extract from the given string, the module of the model and model's class.

        Expected model format: module_name.model_name => hero.Hero
        """
        pkg_name, _, model_name = model_str.partition(".")
        module_path = self.app_dir / pkg_name / "models"
        module_import_path = file_services.linux_path_to_module_path(module_path)

        model_module = import_module(module_import_path)
        model_class = getattr(model_module, model_name)
        return model_module, model_class

    def _to_instance(self, model_data: ModelDataType) -> T:
        """Transform a dict to the correct model instance.
        Expected yaml structure:
            - model: hero.Hero
              id: 1
              properties:
                name: "Spider-Boy"
                secret_name: "Pedro Parqueador"
        """
        model_module, model_class = self._module_and_class(model_data["model"])
        properties: dict[str, Any] = model_data["properties"]
        properties = self._fill_primary_key(model_data, properties)

        if model_class is None:
            raise ValueError(
                f"Model {model_class.__name__} not found in module: {model_module}."
            )

        return model_class(**properties)

    def _to_instances(self, data_list: list[ModelDataType]) -> list[T]:
        return [self._to_instance(data) for data in data_list]

    async def load(self, data_list: list[ModelDataType]) -> list[T]:
        """Load the given data list to list of model instances."""
