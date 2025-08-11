import asyncio
import json
from http import HTTPStatus
from typing import Annotated

import typer
from httpx import AsyncClient

from core.monitoring.logger import get_logger
from settings import settings

_logger = get_logger(__file__)
app = typer.Typer(rich_markup_mode="rich")


async def _health_check(liveness: bool, readiness: bool):
    async with AsyncClient() as client:
        query = {}
        if liveness:
            query["liveness"] = True
        elif readiness:
            query["readiness"] = True

        response = await client.get(settings.health_check_endpoint, params=query)
        if response.status_code >= HTTPStatus.BAD_REQUEST:
            raise RuntimeError(
                f"Health check failed with status code {response.status_code}, {response.text}"
            )
        _logger.info(json.dumps(response.json()))


@app.command(name="healthcheck", help="Check the health of the application")
def health_check(
    liveness: Annotated[
        bool,
        typer.Option(
            "--liveness",
            "-l",
            help="Check that the application (without dependencies) is functional.",
        ),
    ] = True,
    readiness: Annotated[
        bool,
        typer.Option(
            "--readiness",
            "-r",
            help="Check that the entire application is functional. the application and its dependencies.",
        ),
    ] = False,
):
    return asyncio.run(_health_check(liveness, readiness))
