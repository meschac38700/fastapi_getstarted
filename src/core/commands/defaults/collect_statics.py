from typing import Annotated

import typer

from core.monitoring.logger import get_logger
from core.services.runners.collect_statics import CollectStaticFiles
from core.types.annotations.command_types import typer_list_options

_logger = get_logger(__file__)
app = typer.Typer(rich_markup_mode="rich")

AppNames = typer_list_options(
    "--apps",
    "-a",
    help_msg="Specify some application names where to collect static files.",
)


@app.command(name="collectstatic", help="Load project fixtures.")
def collect_statics(
    app_names: AppNames,
    clear: Annotated[
        bool,
        typer.Option(
            "--clear",
            "-c",
            help="if True, all previous collected files will be clear before collecting again.",
        ),
    ] = False,
):
    _logger.info("Collecting static files...")

    collect_static_runner = CollectStaticFiles(p_logger=_logger)
    collect_static_runner(clear=clear, app_names=app_names)
