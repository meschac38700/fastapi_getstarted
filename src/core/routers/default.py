import secrets

from celery import states as celery_states
from fastapi import FastAPI

from apps.user.models import User
from core.monitoring.logger import get_logger
from core.tasks import load_fixtures_task
from redis import asyncio as aioredis
from settings import settings

_logger = get_logger(__name__)


async def health_check():
    # check that the database is up
    await User.count()

    # check that redis is up
    redis = aioredis.from_url(settings.celery_broker)
    await redis.ping()

    return {"status": "ok"}


def secret_key(length: int = 65):
    secret = secrets.token_urlsafe(length)
    return {"secret": secret}


def load_fixtures():
    response = {
        "status": celery_states.FAILURE,
        "msg": "Loading fixtures process finished.",
        "loaded": 0,
    }
    try:
        count_loaded: int = load_fixtures_task.delay().get(timeout=10)
        response["status"] = celery_states.SUCCESS
        response["loaded"] = count_loaded
    except Exception as e:
        if "sqlalchemy.exc.IntegrityError" in str(e):
            response["status"] = celery_states.REJECTED
            _logger.debug("IntegrityError during load fixtures task.", exc_info=e)
        else:
            _logger.debug("An error occurred during load fixtures task.", exc_info=e)

    return response


def register_default_endpoints(app: FastAPI):
    default_tags = ["Default"]
    default_endpoints = [
        {
            "path": "/",
            "endpoint": secret_key,
            "methods": ["GET"],
            "name": "secret_key",
            "tags": default_tags,
        },
        {
            "path": "/healthcheck",
            "endpoint": health_check,
            "methods": ["GET"],
            "name": "health_check",
            "tags": default_tags,
        },
        {
            "path": "/fixtures",
            "endpoint": load_fixtures,
            "methods": ["POST"],
            "name": "fixtures",
            "tags": default_tags,
        },
    ]
    for endpoint in default_endpoints:
        app.router.add_api_route(**endpoint)
