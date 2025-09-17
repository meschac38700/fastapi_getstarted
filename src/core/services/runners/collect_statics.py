import logging
import shutil

from core.monitoring.logger import get_logger
from core.services.files import apps as app_utils
from core.services.files import paths as path_utils
from settings import settings

_logger = get_logger(__name__)


class CollectStaticFiles:
    def __init__(self, p_logger: logging.Logger = None):
        self.logger = p_logger or _logger
        self.static_file_folder = settings.static_path

    def __call__(self, *, clear: bool = False, app_names: list[str] = None):
        if clear:
            self._clear_static_files()

        if app_names:
            static_paths = self._get_app_static_paths(app_names)
        else:
            static_paths = [
                app_items[0] + ".statics" for app_items in app_utils.static_packages()
            ]

        if not static_paths:
            self.logger.info("No static files found to collect: {app_names=}")
            return None

        return self.collect_static_files(static_paths)

    def collect_static_files(self, static_paths: list[str] = None):
        self.logger.info(f"Prepare to collect staticfiles from: {static_paths}")
        static_folder_paths = {
            path_utils.resolve_module_path(static_path) for static_path in static_paths
        }
        for static_folder__path in static_folder_paths:
            for static_subfolder in static_folder__path.iterdir():
                shutil.copytree(
                    static_subfolder,
                    settings.static_path / static_subfolder.name,
                    dirs_exist_ok=True,
                )
                self.logger.info(
                    f"Staticfiles collected from: {static_subfolder.relative_to(settings.BASE_DIR)}"
                )

    def _clear_static_files(self):
        self.logger.info("Clearing previous collected static files...")
        count = 0
        for child in settings.static_path.iterdir():
            count += 1
            if child.is_dir():
                shutil.rmtree(child)
                continue

            child.unlink()

        self.logger.info(f"{count} static files were deleted.")

    def _get_app_static_paths(self, app_names: list[str]) -> list[str]:
        static_folders = []
        for app_name in app_names:
            static_module_path = app_utils.resolve_app_name(
                app_name, settings.STATIC_ROOT
            )
            if static_module_path is None:
                self.logger.info(
                    f"Skipping app '{app_name}' as no static module found."
                )
                continue
            static_folders.append(static_module_path + "." + settings.STATIC_ROOT)
        return static_folders
