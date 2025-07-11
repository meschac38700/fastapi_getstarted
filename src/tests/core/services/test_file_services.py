from pathlib import Path

import pytest

import settings
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
