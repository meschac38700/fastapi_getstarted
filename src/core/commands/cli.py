import typer

from .defaults import (
    fixture_command,
    health_check_command,
    server_command,
    test_command,
)
from .utils import AppCommandRegisterManager

app = typer.Typer(rich_markup_mode="rich")

# TODO(Eliam): improve that load system
app.add_typer(test_command)
app.add_typer(server_command)
app.add_typer(fixture_command)
app.add_typer(health_check_command)

command_manager = AppCommandRegisterManager(app)
command_manager.register()


def main():
    app()
