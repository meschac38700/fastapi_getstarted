from pathlib import Path

import pytest
from sqlmodel.main import SQLModelMetaclass

import settings
from core.services.files import retrieve_all_app_models
from core.services.files.apps import extract_app_name_from_path


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
