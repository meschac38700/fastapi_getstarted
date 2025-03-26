import glob
from pathlib import Path
from typing import Any, Generator

import settings


def _has_router_module(module_folder_path: Path) -> bool:
    """Check if the given module path is valid.

    A valid module folder should contain a routers module/package.
    """
    routers_module_name = "routers"
    return any(
        [
            (module_folder_path / routers_module_name).exists(),  # pkg
            (module_folder_path / (routers_module_name + ".py")).exists(),  # module
        ]
    )


def get_application_paths() -> Generator[Path, Any, None]:
    """Retrieve all create applications from apps package."""
    module_paths = glob.glob(str(settings.BASE_DIR / "apps" / "*"))

    for module_path_str in module_paths:
        module_path = Path(module_path_str)
        if _has_router_module(module_path):
            yield module_path
