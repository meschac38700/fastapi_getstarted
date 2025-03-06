import glob
from typing import Sequence

import settings

app_dir = settings.BASE_DIR / "apps"


def collect_app_fixtures(app_name: str) -> Sequence[str]:
    fixture_dir = app_dir / app_name / "fixtures"
    if not fixture_dir.is_dir():
        raise ValueError(f"App {app_name} do not have fixture module.")

    return glob.glob(str(fixture_dir / "*.y*ml"))


def retrieve_app_fixtures(app_names: Sequence[str]):
    fixtures = []
    for app_name in app_names:
        app_fixtures = collect_app_fixtures(app_name)
        fixtures.extend(app_fixtures)

    return fixtures
