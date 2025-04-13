from pathlib import Path

import typer
from celery.result import AsyncResult

from core.monitoring.logger import get_logger
from core.tasks import load_fixtures_task
from core.types.annotations.command_types import TyperListOption

_logger = get_logger(__file__)
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
    result: AsyncResult = load_fixtures_task.delay(apps, names, paths)

    try:
        count_created = result.get(timeout=2)
    except RuntimeError as e:
        count_created = 0
        _logger.error(f"Something goes wrong while loading fixtures.\n{e}\n")
        _logger.info(
            "This issue is usually caused by an attempt to duplicate data. Check if the data is already stored in the database."
        )

    _logger.info(f"Loaded {count_created} fixtures successfully.")
