import asyncio
import logging
from pathlib import Path

import typer

from core.commands.defaults.runners.fixture import FixtureRunner
from core.types.annotations.command_types import TyperListOption

_logger = logging.Logger(__file__)
app = typer.Typer(rich_markup_mode="rich")

AppsType = TyperListOption(
    "Specify some applications for which the fixtures should be loaded. Default loading initial_fixtures."
)
NamesType = TyperListOption("Name of the fixtures to load. ex: --names initial-users")
PathsType = TyperListOption("List of fixture file paths to load", of_type=Path)


@app.command(help="Load project fixtures.")
def fixtures(
    apps: AppsType,
    names: NamesType,
    paths: PathsType,
):
    """Load project fixtures."""
    runner = FixtureRunner(logger=_logger)

    # TODO(Eliam): Typer does not yet support async command
    #  Issue: https://github.com/fastapi/typer/issues/950
    asyncio.run(runner(app_names=apps, fixture_names=names, fixture_paths=paths))
