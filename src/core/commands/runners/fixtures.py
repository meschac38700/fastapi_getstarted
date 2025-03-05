import asyncio
import logging
from typing import Annotated

import typer
from sqlalchemy.exc import IntegrityError

from core.commands.runners.utils.fixtures import retrieve_app_fixtures
from core.db.fixtures import LoadFixtures

_logger = logging.Logger(__file__)
app = typer.Typer(rich_markup_mode="rich")


@app.command(help="Load project fixtures.")
def load_fixtures(
    names: Annotated[
        list[str],
        typer.Option(
            help="Specify some applications for which the fixtures should be loaded. Default loading initial_fixtures."
        ),
    ] = None,
):
    """Load project fixtures."""

    fixtures = []
    if names:
        fixtures = retrieve_app_fixtures(names)

    fixture_loader = LoadFixtures(logger=_logger)
    try:
        # TODO(Eliam): Typer does not support async command yet
        #  Issue: https://github.com/fastapi/typer/issues/950
        asyncio.run(fixture_loader.load_fixtures(fixtures))
    except IntegrityError:
        _logger.info(
            "It looks like loading fixtures might cause data integrity issues."
        )
        return
    _logger.info("All fixtures loaded successfully.")
