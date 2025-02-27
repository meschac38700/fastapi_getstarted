import typer

from .tests import app as tests_command
from .utils import AppCommandRegisterManager

app = typer.Typer(rich_markup_mode="rich")

app.add_typer(tests_command)

command_manager = AppCommandRegisterManager(app)
command_manager.register()


def main():
    app()
