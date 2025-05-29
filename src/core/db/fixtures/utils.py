import glob
from pathlib import Path
from typing import Sequence

import settings
from core.services import files as app_utils

app_dir = settings.BASE_DIR / "apps"


def collect_app_fixtures(app_name: str) -> Sequence[str]:
    """Return all fixtures of the given app name."""

    fixture_dir = app_dir / app_name / "fixtures"
    if not fixture_dir.is_dir():
        raise ValueError(f"App {app_name} does not contain any fixtures file.")

    return glob.glob(str(fixture_dir / "*.y*ml"))


def retrieve_app_fixtures(app_names: Sequence[str]):
    """Return sequence of fixture string paths from the given app names."""
    fixtures = []
    for app_name in app_names:
        app_fixtures = collect_app_fixtures(app_name)
        fixtures.extend(app_fixtures)

    return fixtures


def retrieve_fixture_absolute_path(fixture_name: str):
    app_paths = app_utils.get_application_paths(required_module="fixtures")
    for app_path in app_paths:
        fixture_filename = f"{Path(fixture_name).stem}.y*ml"
        fixtures_path = str(Path(app_path) / "**" / fixture_filename)
        if paths := glob.glob(fixtures_path, recursive=True):
            return paths[0]
    return None
