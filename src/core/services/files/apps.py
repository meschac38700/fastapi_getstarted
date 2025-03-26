import glob
from functools import lru_cache
from importlib import import_module
from pathlib import Path
from typing import Any, Generator

from sqlmodel.main import SQLModelMetaclass

import settings

from .paths import linux_path_to_module_path


def contains_module(module_folder_path: Path, *, module_name: str = "routers") -> bool:
    """Check if the given module path contains the specified module_name."""
    return any(
        [
            (module_folder_path / module_name).exists(),  # pkg
            (module_folder_path / (module_name + ".py")).exists(),  # module
        ]
    )


def get_application_paths(
    required_module: str = "routers",
) -> Generator[Path, Any, None]:
    """Retrieve all create applications from apps package."""
    module_paths = glob.glob(str(settings.BASE_DIR / "apps" / "*"))

    for module_path_str in module_paths:
        module_path = Path(module_path_str)
        if contains_module(module_path, module_name=required_module):
            yield module_path


def get_app_models(app_path: Path | str):
    """Retrieve all app model classes from models apps.{app_name}.models module."""
    _app_path = Path(app_path)

    models_module_path = linux_path_to_module_path(_app_path / "models")
    models_module = import_module(models_module_path)
    for model_name in models_module.__all__:
        model_class = getattr(models_module, model_name, None)
        if isinstance(model_class, SQLModelMetaclass):
            yield model_class


@lru_cache
def retrieve_all_app_models():
    return sum(
        [
            list(get_app_models(app_path))
            for app_path in get_application_paths(required_module="models")
        ],
        [],
    )
