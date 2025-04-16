import secrets

from celery.result import AsyncResult
from fastapi import FastAPI

from core.tasks import load_fixtures_task


def secret_key(length: int = 65):
    secret = secrets.token_urlsafe(length)
    return {"secret": secret}


async def load_fake_data():
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
            "path": "/fixtures",
            "endpoint": load_fake_data,
            "methods": ["POST"],
            "name": "fixtures",
            "tags": default_tags,
        },
    ]
    for endpoint in default_endpoints:
        app.router.add_api_route(**endpoint)
