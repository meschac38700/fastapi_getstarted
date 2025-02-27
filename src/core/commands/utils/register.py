from importlib import import_module
from pathlib import Path
from types import ModuleType

import typer

import settings
from core.file_manager import get_application_paths, linux_path_to_module_path


class AppCommandRegisterManager[T = typer.Typer]:  # noqa: E251
    """Get all the subcommands from the application package and save them to the given main command instance."""

    def __init__(self, main_command: T):
        self.main_command = main_command
        self._app_dir = settings.BASE_DIR / "apps"
        self._command_module_name = "commands"
        self._registers_mapping = {
            "typer": self._register_typer_sub_commands,
        }

    def _retrieve_app_command_instances(self):
        """Retrieve all instances of command from the apps' folder."""
        app_paths = get_application_paths()
        for app_path in app_paths:
            command_module = self._get_command_module(app_path)
            if command_module is None:
                continue

            if (cmd_instance := self._get_command_instance(command_module)) is None:
                continue

            app_name = app_path.stem
            yield cmd_instance, app_name

    def _get_command_module(self, app_path: Path):
        command_module_path = app_path / self._command_module_name
        if not command_module_path.exists() or not command_module_path.is_dir():
            return None
        module_path = linux_path_to_module_path(command_module_path)

        return import_module(module_path)

    def _get_command_instance(self, command_module: ModuleType) -> T | None:
        if command_module.__dict__.get("__all__") is None:
            raise ValueError(
                "Invalid command package, it should contain __init__.py file with command instance."
            )

        module_names = command_module.__all__
        for module_name in module_names:
            module = getattr(command_module, module_name)
            if isinstance(module, type(self.main_command)):
                return module

        return None

    def _register_typer_sub_commands(self):
        main_cmd: typer.Typer = self.main_command
        for sub_command, app_name in self._retrieve_app_command_instances():
            _help = f"Manage {app_name} in the app. Use --help option to see the different possible commands."
            main_cmd.add_typer(sub_command, name=app_name, help=_help)

    def register(self, package: str = "typer"):
        register_sub_commands = self._registers_mapping.get(package)
        return register_sub_commands()
