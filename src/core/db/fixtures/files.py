import re
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any, AsyncIterable, Generator, TypedDict

import settings
from apps.authorization.models import Permission
from core.db import SQLTable
from core.services.files import YAMLReader


class ModelDataType(TypedDict):
    model: str
    id: int
    properties: dict[str, Any]


@dataclass
class FixtureFileReader(YAMLReader):
    app_dir: Path | None = settings.BASE_DIR / "apps"

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

    async def _fix_permissions(self, properties: dict[str, Any]):
        """Replace permission names to permission instances."""

        _properties = properties.copy()
        if permission_names := set(_properties.get("permissions", [])):
            permissions = await Permission.filter(name__in=permission_names)
            if len(permissions) != len(permission_names):
                missing_perms = [
                    perm.name for perm in permissions if perm.name in permission_names
                ] or permission_names
                self.logger.info(f"Permissions not found: {missing_perms}.")
                raise ValueError(f"Permissions not found: {missing_perms}")

            _properties["permissions"] = permissions
        return _properties

    def _module_and_class(self, model_str: str) -> tuple[ModuleType, type[SQLTable]]:
        """Extract from the given string, the module of the model and model's class.

        Expected model format: module_name.model_name => hero.Hero
        """
        pkg_name, _, model_name = model_str.partition(".")
        package_path = self.app_dir / pkg_name
        module_path = str(package_path / "models").replace(str(settings.BASE_DIR), "")
        module_import_path = re.sub("/", ".", module_path).strip(".")

        model_module = import_module(module_import_path)
        model_class = getattr(model_module, model_name)
        return model_module, model_class

    async def _dict_to_instance(self, model_data: ModelDataType):
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
        properties = await self._fix_permissions(properties)

        if model_class is None:
            raise ValueError(
                f"Model {model_class.__name__} not found in module: {model_module}."
            )

        return model_class(**properties)

    async def models(self) -> AsyncIterable[SQLTable] | Generator[SQLTable, Any, None]:
        return (
            await self._dict_to_instance(model_data)
            for model_data in await self.read_async()
        )
