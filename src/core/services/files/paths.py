from pathlib import Path

import settings


def relative_from_src(path: Path | str) -> str | None:
    """Make relative the give path from src folder.

    example:
     > relative_from_src("/home/user/project/fixtures")
     > "project/fixtures"
    """

    base_dir_path = str(settings.BASE_DIR)
    relative_path = str(path).split(base_dir_path + "/")
    if relative_path:
        return relative_path[-1]
    return None


def linux_path_to_module_path(linux_path: str | Path):
    relative_path = relative_from_src(linux_path)
    if relative_path is None:
        return None

    return relative_path.replace("/", ".").strip(".")
