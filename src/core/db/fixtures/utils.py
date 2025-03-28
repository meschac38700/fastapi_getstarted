import glob
from pathlib import Path
from typing import Iterable, Sequence


def preserve_fixtures_order(app_paths: Iterable[str], fixture_names: Sequence[str]):
    """Make a fixture path generator based on the order of the given fixture names.

    Allows fixtures to be loaded in the specified order.
    Thus, the developer defines the loading order of the fixtures.
    """
    for fixture_name in fixture_names:
        for path in app_paths:
            fixture_name = f"{Path(fixture_name).stem}.y*ml"
            fixtures_path = str(Path(path) / "**" / fixture_name)
            if glob.glob(fixtures_path, recursive=True):
                yield path
