from pathlib import Path

import settings


def linux_path_to_module_path(linux_path: str | Path):
    base_dir_path = str(settings.BASE_DIR)
    module_linux_path = str(linux_path).split(base_dir_path)[-1]
    if not module_linux_path:
        return None

    return module_linux_path.replace("/", ".").strip(".")
