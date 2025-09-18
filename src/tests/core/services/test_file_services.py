import importlib
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
from fastapi import APIRouter
from sqlmodel.main import SQLModelMetaclass

from apps.authentication.models import JWTToken
from apps.authorization.models import (
    Group,
    GroupUserLink,
    Permission,
    PermissionGroupLink,
    PermissionUserLink,
)
from apps.authorization.routers import routers as authorization_routers
from apps.user.models import User
from core.db import SQLTable
from core.services.files import apps as file_app_services
from core.services.files import get_application_paths
from core.services.files import paths as file_path_services
from core.services.files import retrieve_all_app_models
from settings import settings
from tests.core.services.data.models import MyTestModel


@pytest.mark.parametrize(
    "filepath,expected",
    (
        (
            Path(
                settings.BASE_DIR / "apps" / "user" / "fixtures" / "initial_users.yaml"
            ),
            "user",
        ),
        (
            Path(
                settings.BASE_DIR
                / "apps"
                / "authorization"
                / "fixtures"
                / "initial_permissions.yaml"
            ),
            "authorization",
        ),
        (Path(settings.BASE_DIR / "apps"), None),
        (Path(settings.BASE_DIR), None),
    ),
)
def test_extract_app_name_from_path(filepath, expected):
    assert file_app_services.extract_app_name_from_path(filepath) == expected


def test_retrieve_all_app_models():
    models = retrieve_all_app_models()
    assert len(models) > 1
    assert all(isinstance(model, SQLModelMetaclass) for model in models)
    assert all(model.model_config.get("table") for model in models)


@pytest.mark.parametrize(
    "app_path,expected_models",
    (
        (Path(settings.BASE_DIR) / "apps" / "user", [User]),
        (Path(settings.BASE_DIR) / "apps" / "authentication", [JWTToken]),
        (
            Path(settings.BASE_DIR) / "apps" / "authorization",
            [Permission, Group, PermissionUserLink, PermissionGroupLink, GroupUserLink],
        ),
    ),
)
def test_get_models_by_app_path(app_path: Path | str, expected_models):
    actual_models = list(file_app_services.get_models_by_app_path(app_path))
    assert len(actual_models) == len(expected_models)
    assert all(expected_model in actual_models for expected_model in expected_models)


@pytest.mark.parametrize(
    "module,expected_models",
    (
        (importlib.import_module("apps.authentication.models"), [JWTToken]),
        (importlib.import_module("apps.user.models"), [User]),
        (importlib.import_module("tests.core.services.data.models"), [MyTestModel]),
    ),
)
def test_retrieve_module_models(
    module: ModuleType, expected_models: list[SQLModelMetaclass]
):
    actual_models = list(
        file_app_services.retrieve_module_items(
            module, file_app_services.is_valid_model
        )
    )
    assert len(actual_models) == len(expected_models)
    assert all(expected_model in actual_models for expected_model in expected_models)


def test_get_application_paths():
    paths = list(get_application_paths())
    expected_paths = [
        settings.BASE_DIR / "apps" / "authentication",
        settings.BASE_DIR / "apps" / "authorization",
        settings.BASE_DIR / "apps" / "user",
    ]
    assert len(paths) >= len(expected_paths)
    assert all(expected_path in paths for expected_path in expected_paths)


@pytest.mark.parametrize(
    "package_path,required_module,expected",
    (
        (settings.BASE_DIR / "apps" / "user", "models", True),
        (settings.BASE_DIR / "apps" / "authentication", "routers", True),
        (settings.BASE_DIR / "apps" / "authorization", "models", True),
        (settings.BASE_DIR / "apps" / "authorization", "azeaze", False),
    ),
)
def test_is_valid_package(package_path: Path, required_module: str, expected: bool):
    assert (
        file_app_services.is_valid_package(package_path, module_name=required_module)
        is expected
    )


@pytest.mark.parametrize(
    "model_instance,expected",
    (
        (MyTestModel, True),
        (SQLTable, False),
        (ModuleType, False),
    ),
)
def test_is_valid_model(model_instance: SQLModelMetaclass | Any, expected: bool):
    assert file_app_services.is_valid_model(model_instance) is expected


@pytest.mark.parametrize(
    "router_instance,expected",
    (
        (authorization_routers, True),
        (SQLTable, False),
    ),
)
def test_is_valid_router(router_instance: APIRouter | Any, expected: bool):
    assert file_app_services.is_valid_router(router_instance) is expected


@pytest.mark.parametrize(
    "original_path,expected_path",
    (
        (settings.BASE_DIR / "apps" / "authentication", "apps.authentication"),
        (settings.BASE_DIR / "core" / "commands" / "cli.py", "core.commands.cli"),
        (settings.BASE_DIR / "core" / "commands" / "__init__.py", "core.commands"),
    ),
)
def test_linux_path_to_module_path(original_path: Path, expected_path: str):
    assert file_path_services.linux_path_to_module_path(original_path) == expected_path


@pytest.mark.parametrize(
    "original_path,from_path,folder_name,expected_path",
    (
        (
            settings.BASE_DIR / "apps" / "authentication",
            None,
            None,
            Path("apps/authentication"),
        ),
        (
            settings.BASE_DIR / "core" / "commands" / "cli.py",
            None,
            None,
            Path("core/commands/cli.py"),
        ),
        (
            settings.BASE_DIR / "core" / "commands" / "cli.py",
            settings.BASE_DIR / "core" / "commands",
            None,
            Path("cli.py"),
        ),
        (
            settings.BASE_DIR / "core" / "commands" / "cli.py",
            None,
            "commands",
            Path("cli.py"),
        ),
        (
            settings.BASE_DIR / "core" / "commands" / "commands" / "cli.py",
            None,
            "commands",
            Path("commands/cli.py"),
        ),
        (settings.BASE_DIR / "core" / "commands" / "cli.py", None, "cli.py", Path(".")),
        (settings.BASE_DIR / "cli.py", settings.BASE_DIR / "cli.py", None, Path(".")),
        (Path("/foo/bar"), None, None, Path("/foo/bar")),
    ),
)
def test_relative_from(
    original_path: Path, from_path: Path, folder_name: str, expected_path: str
):
    assert (
        file_path_services.relative_from(
            original_path, from_path=from_path, folder_name=folder_name
        )
        == expected_path
    )


@pytest.mark.parametrize(
    "module_path,expected_path",
    (
        (
            "apps.user.models.user",
            settings.BASE_DIR / "apps" / "user" / "models" / "user.py",
        ),
        ("apps.user.fixtures", settings.BASE_DIR / "apps" / "user" / "fixtures"),
        ("foo.bar", None),
    ),
)
def test_resolve_module_path(module_path: str, expected_path: Path):
    assert file_path_services.resolve_module_path(module_path) == expected_path


@pytest.mark.parametrize(
    "app_name,required_module,expected_module",
    (
        ("user", "models", "apps.user"),
        ("user", "foo", None),
    ),
)
def test_resolve_app_name(app_name: str, required_module: str, expected_module: str):
    assert (
        file_app_services.resolve_app_name(app_name, required_module) == expected_module
    )
