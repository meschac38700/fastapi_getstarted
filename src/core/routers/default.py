import secrets

from fastapi import FastAPI

from core.db.fixtures import LoadFixtures


def secret_key(length: int = 65):
    secret = secrets.token_urlsafe(length)
    return {"secret": secret}


async def load_fake_data():
    await LoadFixtures().load_fixtures()
    return {"Loaded": True}


async def sentry_debug():
    return 1 / 0


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
        {
            "path": "/sentry-debug",
            "endpoint": sentry_debug,
            "methods": ["GET"],
            "name": "sentry",
            "tags": default_tags,
        },
    ]
    for endpoint in default_endpoints:
        app.router.add_api_route(**endpoint)
