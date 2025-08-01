from pathlib import Path

import typer
from celery.result import AsyncResult

from core.monitoring.logger import get_logger
from core.tasks import load_fixtures_task
from core.types.annotations.command_types import typer_list_options

_logger = get_logger(__file__)
app = typer.Typer(rich_markup_mode="rich")

AppsType = typer_list_options(
    "--apps",
    "-a",
    help_msg="Specify some applications for which the fixtures should be loaded. Default loading initial_fixtures.",
)
NamesType = typer_list_options(
    "--names",
    "-n",
    help_msg="Name of the fixtures to load. ex: --names initial-users",
)
PathsType = typer_list_options(
    "--paths", "-p", help_msg="List of fixture file paths to load", of_type=Path
)


@app.command(help="Load project fixtures.")
def fixtures(
    apps: AppsType,
    names: NamesType,
    paths: PathsType,
):
    """Load project fixtures."""
    _logger.info("Load fixtures command starting...")
    result: AsyncResult = load_fixtures_task.delay(
        apps, names, [str(p) for p in paths or []]
    )

    try:
        count_created = result.get(timeout=2)
    except RuntimeError as e:
        count_created = 0
        _logger.error(f"Something goes wrong while loading fixtures.\n{e}\n")
        _logger.info(
            "This issue is usually caused by an attempt to duplicate data. Check if the data is already stored in the database."
        )

    _logger.info(f"Loaded {count_created} fixtures successfully.")
    return count_created
