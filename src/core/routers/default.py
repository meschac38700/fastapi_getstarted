import secrets

from celery.result import AsyncResult
from fastapi import FastAPI

from apps.user.models import User
from core.tasks import load_fixtures_task
from redis import asyncio as aioredis
from settings import settings


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


def load_fake_data():
    result: AsyncResult = load_fixtures_task.delay()
    return {
        "status": result.state,
        "msg": "Loading fixtures process started.",
        "success": result.successful(),
    }


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
            "endpoint": load_fake_data,
            "methods": ["POST"],
            "name": "fixtures",
            "tags": default_tags,
        },
    ]
    for endpoint in default_endpoints:
        app.router.add_api_route(**endpoint)
