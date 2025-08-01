import importlib
from pathlib import Path
from types import ModuleType
from typing import Literal

from fastapi import APIRouter, FastAPI

from core.monitoring.logger import get_logger
from core.services.files import apps as file_apps
from core.services.files import linux_path_to_module_path
from settings import settings

_logger = get_logger(__name__)


class AppRouter:
    """Register all routers found in the apps/ directory, respecting the correct structure of the applications.

    correct app structure:
    apps
        └── hero
            ├── fixtures
            │   └── initial-heroes.yaml
            ├── models
            │   └── __init__.py
            └── routers.py (OR a package with an export router instance of APIRouter in __init__.py file)
            └── web.py (OR a package with an export router instance of APIRouter in __init__.py file)
    """

    def __init__(self):
        self.routers_module_name = "routers"
        self.web_module_name = "web"
        self.app_pkg_name = "apps"
        self.api_main_router = APIRouter(prefix=settings.API_ROUTER_PREFIX)
        self.web_main_router = APIRouter(prefix=settings.WEB_ROUTER_PREFIX)

    def _import_router_modules(self, module_path: Path):
        """Prepare and import router modules (convention: web.py or routers.pu)."""
        router_modules: list[ModuleType | None] = [None, None]

        _router_module_path = module_path / self.routers_module_name
        if file_apps.is_valid_package(
            module_path, module_name=self.routers_module_name
        ):
            _router_module_path = linux_path_to_module_path(_router_module_path)
            router_modules[0] = importlib.import_module(_router_module_path)

        _web_module_path = module_path / self.web_module_name
        if file_apps.is_valid_package(module_path, module_name=self.web_module_name):
            _web_module_path = linux_path_to_module_path(_web_module_path)
            router_modules[1] = importlib.import_module(_web_module_path)

        return router_modules

    def _module_routers_registration(
        self,
        routers: list[APIRouter],
        *,
        module_path: Path,
        router_type: Literal["api", "web"] = "api",
    ):
        # extract module name, to be used as router prefix
        if not routers:
            return

        main_router = self.api_main_router
        if router_type == "web":
            main_router = self.web_main_router

        prefix = f"/{module_path.stem}"
        for router in routers:
            if router.prefix:
                prefix = ""
            main_router.include_router(router, prefix=prefix)

    def register_all(self, app: FastAPI):
        """Register all routers from apps folder."""
        for module_path in file_apps.get_application_paths():
            router_module, web_module = self._import_router_modules(module_path)

            if not any((router_module, web_module)):
                _logger.info(f"No router was found in {module_path}")
                continue

            if router_module is not None:
                api_routers = list(
                    file_apps.retrieve_module_items(
                        router_module, file_apps.is_valid_router
                    )
                )
                self._module_routers_registration(
                    api_routers, module_path=module_path, router_type="api"
                )

            if web_module is not None:
                web_routers = list(
                    file_apps.retrieve_module_items(
                        web_module, file_apps.is_valid_router
                    )
                )
                self._module_routers_registration(
                    web_routers, module_path=module_path, router_type="web"
                )

        app.include_router(self.api_main_router)
        app.include_router(self.web_main_router)
