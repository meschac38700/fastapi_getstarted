from pathlib import Path

import settings

_Path = Path | str


def relative_from(p_path: _Path, from_folder: _Path = None) -> Path:
    """Make the given path relative to the provided 'from_folder'. The default is "src".

    example:
     > relative_from("/home/user/project/fixtures")
     > "project/fixtures"
    """

    base_dir = from_folder or settings.BASE_DIR
    try:
        return p_path.relative_to(base_dir)
    except ValueError:
        return p_path


def linux_path_to_module_path(linux_path: _Path) -> str:
    """Normalize a path to a Python module path."""
    relative_path = str(relative_from(linux_path))
    return relative_path.replace("/", ".").strip(".")
