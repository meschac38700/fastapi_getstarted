import glob
import importlib
import re
from pathlib import Path

from fastapi import FastAPI

from settings import BASE_DIR


def register_app_routers(app: FastAPI):
    """Register all routers from apps folder."""
    router_path = "routers"
    app_folder = "apps/"
    router_module = "routers"
    for module_path_str in glob.glob(str(BASE_DIR / app_folder / "*")):
        module_path = Path(module_path_str)
        # check is valid package (contains routers module)
        if not any(
            [
                (module_path / router_path).exists(),
                (module_path / (router_path + ".py")).exists(),
            ]
        ):
            continue

        # extract module name as router prefix
        prefix = f"/{module_path.stem}"
        # prepare and import router
        module_path = (
            app_folder + f"{module_path}.{router_module}".split(app_folder)[-1]
        )
        module_path = re.sub("/", ".", module_path).strip(".")
        router_module = importlib.import_module(module_path)

        if router_module.routers.prefix:
            prefix = ""

        app.include_router(router_module.routers, prefix=prefix)
