import re
from pathlib import Path

from settings import settings

_Path = Path | str


def relative_from(
    p_path: _Path, *, from_path: Path = None, folder_name: str = None
) -> Path:
    """Make the given path relative to the provided 'from_folder'. The default is "src".

    :param p_path: Path to make relative to one of the provided folders: 'from_folder' or from_path
    :param from_path: Path root from which the given path should be relative
    :param from_folder: Name of the folder to which the given path should be relative

    :return: Relative path

    Example:
     > relative_from("/home/user/project/fixtures")
     > "project/fixtures"
    """
    if folder_name is not None:
        _, __, relative_path = str(p_path).partition(f"{folder_name}")
        return Path(relative_path.lstrip("/"))

    base_dir = Path(from_path) if from_path else settings.BASE_DIR
    try:
        return p_path.relative_to(base_dir)
    except ValueError:
        return p_path


def linux_path_to_module_path(linux_path: _Path) -> str:
    """Normalize a path to a valid importable Python module path."""
    _linux_path = linux_path
    if linux_path.name in ["__init__.py"]:
        _linux_path = linux_path.parent

    relative_path = str(relative_from(_linux_path))

    # remove extension
    ext_pattern = r"\.\w+$"
    relative_path = re.sub(ext_pattern, "", relative_path)

    return relative_path.replace("/", ".").strip(".")
