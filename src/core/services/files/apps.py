import glob
from functools import lru_cache
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Generator, Iterable, ParamSpec

from fastapi import APIRouter
from sqlmodel.main import SQLModelMetaclass

from settings import settings

from . import paths as path_utils

P = ParamSpec("P")
Fn = Callable[[P], Any]


def is_valid_package(package_path: Path, *, module_name: str = "routers") -> bool:
    """Check if the given package path contains the specified module name."""
    return any(
        [
            (package_path / module_name).exists(),  # pkg
            (package_path / (module_name + ".py")).exists(),  # module
        ]
    )


def is_valid_model(model_instance: SQLModelMetaclass | Any) -> bool:
    """Check if the given model is a valid SQLModelMetaclass."""

    is_table = getattr(model_instance, "model_config", {}).get("table", False)
    return isinstance(model_instance, SQLModelMetaclass) and is_table


def is_valid_router(router_instance: APIRouter | Any) -> bool:
    """Check if the given instance is a valid APIRouter.

    Should:
        be instanced of APIRouter

    Regarding FastAPI's current design (as of FastAPI v0.110+ and up through July 2025):

        A valid APIRouter should be an instance of APIRouter.
        Since FastAPI does not implement a parent/child relationship system for APIRouters,
        one possible way to infer hierarchy is by examining router prefixes.
        However, in practice, we haven't encountered scenarios where
        a package would export both nested and parent APIRouters in all,
        nor have we seen modules exporting multiple APIRouters where some are nested.
        Typically, if several APIRouters are exported, they are all at the top level,
        not nested within each other.
    """
    return isinstance(router_instance, APIRouter)


def get_application_paths(
    required_module: str = "routers",
) -> Generator[Path, Any, None]:
    """Retrieve all create applications from apps package."""
    app_packages = glob.glob(str(settings.apps_folder / "*"))

    for app_package_str in app_packages:
        app_package = Path(app_package_str)
        if is_valid_package(app_package, module_name=required_module):
            yield app_package


def retrieve_module_items[T](
    module: ModuleType, matching_callback: Fn
) -> Generator[T, Any, None]:
    """Retrieve all elements of a module/package that are evaluated positively by the given callback.

    If 'module' is a package and not a module (module.py), we will use the __all__ variable
    (which is normally defined in the package/__init__.py module).
    """

    # try the package approach first
    module_names: Iterable[str] = getattr(module, "__all__", [])

    if not module_names:
        # module is not a package but a module
        module_items = dir(module)
        module_names = [
            item_name for item_name in module_items if not item_name.startswith("_")
        ]

    for item_name in module_names:
        item = getattr(module, item_name)
        if matching_callback(item):
            yield item


def get_models_by_app_path(app_path: Path):
    """Retrieve all models defined in apps/{app_name}/models module or package."""
    models_module_path = path_utils.linux_path_to_module_path(app_path / "models")
    models_module = import_module(models_module_path)

    return retrieve_module_items(models_module, is_valid_model)


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
    app_dir = settings.apps_folder
    try:
        relative_path = file_path.relative_to(app_dir)
        app_name = str(relative_path).split("/")[0]
        if app_name == ".":
            return None
        return app_name
    except ValueError:
        return None


def static_packages() -> list[tuple[str, str]]:
    """Return list of static packages for each application inside apps package."""
    app_paths = get_application_paths(required_module=settings.STATIC_ROOT)

    return [
        (path_utils.linux_path_to_module_path(app_path), settings.STATIC_ROOT)
        for app_path in app_paths
    ]


def retrieve_template_tags():
    """Retrieve all defined template tags.

    First get tags from core.templating.templatetags
    then go through apps folder and extract all tags from templatetags folder.
    TODO(Eliam): Re-work on this, make a global register system
     like Django Library(django.template.Library)
    """
    core_tags_path = settings.BASE_DIR / "core/templating/templatetags"
    core_tags_module = import_module(
        path_utils.linux_path_to_module_path(core_tags_path)
    )
    all_tags = [
        getattr(core_tags_module, tag_name) for tag_name in core_tags_module.__all__
    ]

    for app_path in get_application_paths(required_module="templatetags"):
        # For now, we assume that the tags have been exported in the init file,
        # but later with the library system, we will move to a "registration" approach.
        module_path = path_utils.linux_path_to_module_path(app_path / "templatetags")
        tag_module = import_module(module_path)
        all_tags.extend(
            [getattr(tag_module, tag_name) for tag_name in tag_module.__all__]
        )
    return all_tags


def resolve_app_name(app_name: str, required_module: str) -> str | None:
    """Resolve app name to a valid python module path."""
    app_root = settings.apps_folder
    app_path = app_root / app_name
    if is_valid_package(app_path, module_name=required_module):
        return path_utils.linux_path_to_module_path(app_path)
    return None
