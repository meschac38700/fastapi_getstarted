import asyncio
import json
from http import HTTPStatus

import typer
from httpx import AsyncClient

from core.monitoring.logger import get_logger
from settings import settings

_logger = get_logger(__file__)
app = typer.Typer(rich_markup_mode="rich")


async def _health_check():
    async with AsyncClient() as client:
        response = await client.get(settings.health_check_endpoint)
        if response.status_code >= HTTPStatus.BAD_REQUEST:
            raise RuntimeError(
                f"Health check failed with status code {response.status_code}, {response.text}"
            )
        _logger.info(json.dumps(response.json()))


@app.command(name="healthcheck", help="Check the health of the application")
def health_check():
    return asyncio.run(_health_check())
