import glob
from functools import lru_cache
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any, Generator, Iterable

from sqlmodel.main import SQLModelMetaclass

import settings

from .paths import linux_path_to_module_path


def is_valid_package(package_path: Path, *, module_name: str = "routers") -> bool:
    """Check if the given package path contains the specified module name."""
    return any(
        [
            (package_path / module_name).exists(),  # pkg
            (package_path / (module_name + ".py")).exists(),  # module
        ]
    )


def get_application_paths(
    required_module: str = "routers",
) -> Generator[Path, Any, None]:
    """Retrieve all create applications from apps package."""
    app_packages = glob.glob(str(settings.BASE_DIR / "apps" / "*"))

    for app_package_str in app_packages:
        app_package = Path(app_package_str)
        if is_valid_package(app_package, module_name=required_module):
            yield app_package


def get_models_from_module(module: ModuleType) -> Generator[str, Any, None]:
    """Retrieve all models from a module."""

    module_items = getattr(module, "__dict__", [])
    for item_name in module_items:
        if item_name.startswith("_"):
            continue

        potential_model = module_items[item_name]
        model_config = getattr(potential_model, "model_config", None)
        if model_config is None:
            continue

        if model_config.get("table"):
            yield item_name


def retrieve_module_models(
    models_module: ModuleType,
) -> Generator[SQLModelMetaclass, Any, None]:
    """Retrieve models from a module or package."""

    # models is a package
    model_names: Iterable[str] = getattr(models_module, "__all__", [])

    if not model_names:
        # models is a module
        model_names = get_models_from_module(models_module)

    for model_name in model_names:
        model_instance = getattr(models_module, model_name)
        is_table = getattr(model_instance, "model_config", {}).get("table")
        if isinstance(model_instance, SQLModelMetaclass) and is_table:
            yield model_instance


def get_models_by_app_path(app_path: Path):
    """Retrieve all models defined in apps/{app_name}/models module or package."""
    models_module_path = linux_path_to_module_path(app_path / "models")
    models_module = import_module(models_module_path)
    return retrieve_module_models(models_module)


@lru_cache
def retrieve_all_app_models():
    return sum(
        [
            list(get_models_by_app_path(app_path))
            for app_path in get_application_paths(required_module="models")
        ],
        [],
    )


def extract_app_name_from_path(file_path: Path):
    """Extract app name from the given fixture path."""
    app_dir = settings.BASE_DIR / "apps/"
    try:
        relative_path = file_path.relative_to(app_dir)
        app_name = str(relative_path).split("/")[0]
        if app_name == ".":
            return None
        return app_name
    except ValueError:
        return None
