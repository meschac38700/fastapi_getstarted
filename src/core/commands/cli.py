import typer

from .runners import dev_server_command, fixture_command, test_command
from .utils import AppCommandRegisterManager

app = typer.Typer(rich_markup_mode="rich")

app.add_typer(test_command)
app.add_typer(dev_server_command)
app.add_typer(fixture_command)

command_manager = AppCommandRegisterManager(app)
command_manager.register()


def main():
    app()
