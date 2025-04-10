import logging
from pathlib import Path

import typer

from core.tasks import task_load_fixtures
from core.types.annotations.command_types import TyperListOption

_logger = logging.Logger(__file__)
app = typer.Typer(rich_markup_mode="rich")

AppsType = TyperListOption(
    "--apps",
    "-a",
    description="Specify some applications for which the fixtures should be loaded. Default loading initial_fixtures.",
)
NamesType = TyperListOption(
    "--names",
    "-n",
    description="Name of the fixtures to load. ex: --names initial-users",
)
PathsType = TyperListOption(
    "--paths", "-p", description="List of fixture file paths to load", of_type=Path
)


@app.command(help="Load project fixtures.")
def fixtures(
    apps: AppsType,
    names: NamesType,
    paths: PathsType,
):
    """Load project fixtures."""
    _logger.info("Load fixtures command starting...")
    task_load_fixtures.delay(apps, names, paths)
