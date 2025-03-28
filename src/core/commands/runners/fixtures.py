import asyncio
import logging
from pathlib import Path
from typing import Annotated

import typer
from sqlalchemy.exc import IntegrityError

from core.commands.runners.utils.fixtures import retrieve_app_fixtures
from core.db.fixtures import LoadFixtures

_logger = logging.Logger(__file__)
app = typer.Typer(rich_markup_mode="rich")


@app.command(help="Load project fixtures.")
def fixtures(
    names: Annotated[
        list[str],
        typer.Option(
            help="Specify some applications for which the fixtures should be loaded. Default loading initial_fixtures."
        ),
    ] = None,
    fixture_paths: Annotated[
        list[Path], typer.Option(help="List of fixture file paths to load.")
    ] = None,
):
    """Load project fixtures."""
    fixture_loader = LoadFixtures(logger=_logger)

    _fixtures = [str(fixture_path.absolute()) for fixture_path in fixture_paths or []]
    if names and not _fixtures:
        _fixtures = retrieve_app_fixtures(names)

    try:
        # TODO(Eliam): Typer does not yet support async command
        #  Issue: https://github.com/fastapi/typer/issues/950
        asyncio.run(
            fixture_loader.load_fixtures(_fixtures, is_path=bool(fixture_paths))
        )
    except IntegrityError:
        _logger.info(
            "It looks like loading fixtures might cause data integrity issues."
        )
        return
    _logger.info("All fixtures loaded successfully.")
