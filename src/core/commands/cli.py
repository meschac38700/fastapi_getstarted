import typer

from . import defaults as default_commands
from .utils import AppCommandRegisterManager

app = typer.Typer(rich_markup_mode="rich")

for command_name in default_commands.__all__:
    command_instance = default_commands.__dict__[command_name]
    app.add_typer(command_instance)

command_manager = AppCommandRegisterManager(app)
command_manager.register()


def main():
    app()
