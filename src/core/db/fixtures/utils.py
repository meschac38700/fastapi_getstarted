import glob
from pathlib import Path
from typing import Iterable, Sequence


def preserve_fixtures_order(app_paths: Iterable[str], fixture_names: Sequence[str]):
    """Make a fixture path generator based on the order of the given fixture names.

    Allows fixtures to be loaded in the specified order.
    Thus, the developer defines the loading order of the fixtures.
    """
    paths = list(app_paths)
    for fixture_name in fixture_names:
        for path in paths:
            fixture_name = f"{Path(fixture_name).stem}.y*ml"
            fixtures_path = str(Path(path) / "**" / fixture_name)
            fixtures = glob.glob(fixtures_path, recursive=True)
            if fixtures:
                yield path
