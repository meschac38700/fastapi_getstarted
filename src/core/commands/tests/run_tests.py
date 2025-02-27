from typing import Annotated

import typer

app = typer.Typer(rich_markup_mode="rich")


@app.command(help="Run application tests.")
def tests(
    app_name: Annotated[
        str | None,
        typer.Argument(help="Specify an application name on which to run tests."),
    ] = None,
):
    """Execute application tests."""
    # TODO(Eliam): implement the logic

    if app_name is None:
        print("Running tests with docker.")
        return
    print(f"Running {app_name} tests")
