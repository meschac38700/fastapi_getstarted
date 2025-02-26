import typer

from .tests import app as tests_command

app = typer.Typer(rich_markup_mode="rich")

app.add_typer(tests_command)


def main():
    app()
