import importlib
from pathlib import Path

from fastapi import FastAPI

from core.services.files import (
    get_application_paths,
    linux_path_to_module_path,
)


class AppRouter:
    """Register all routers found in the apps/ directory, respecting the correct structure of the applications.

    correct app structure:
    apps
        └── hero
            ├── fixtures
            │   └── initial-heroes.yaml
            ├── models
            │   └── __init__.py
            └── routers.py (OR module and routers variable should be named/export as 'routers')
    """

    def __init__(self):
        self.routers_module_name = "routers"
        self.app_pkg_name = "apps"

    def _import_router_module(self, module_path: Path):
        """Prepare and import router module."""
        _module_path = module_path / self.routers_module_name
        _module_path = linux_path_to_module_path(_module_path)

        return importlib.import_module(_module_path)

    def register_all(self, app: FastAPI):
        """Register all routers from apps folder."""
        for module_path in get_application_paths():
            # extract module name, to be used as router prefix
            prefix = f"/{module_path.stem}"

            router_module = self._import_router_module(module_path)
            if router_module.routers.prefix:
                prefix = ""

            app.include_router(router_module.routers, prefix=prefix)
