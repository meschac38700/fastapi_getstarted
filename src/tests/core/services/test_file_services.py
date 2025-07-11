import importlib
from pathlib import Path
from types import ModuleType

import pytest
from sqlmodel.main import SQLModelMetaclass

import settings
from apps.authentication.models import JWTToken
from apps.authorization.models import (
    Group,
    GroupUserLink,
    Permission,
    PermissionGroupLink,
    PermissionUserLink,
)
from apps.user.models import User
from core.services.files import get_application_paths, retrieve_all_app_models
from core.services.files.apps import (
    extract_app_name_from_path,
    get_models_by_app_path,
    retrieve_module_models,
)
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
    assert extract_app_name_from_path(filepath) == expected


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
    actual_models = list(get_models_by_app_path(app_path))
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
    actual_models = list(retrieve_module_models(module))
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
