import secrets

from fastapi import FastAPI

from core.db.fixtures import LoadFixtures


def secret_key(length: int = 65):
    secret = secrets.token_urlsafe(length)
    return {"secret": secret}


async def load_fake_data():
    await LoadFixtures().load_fixtures()
    return {"Loaded": True}


base_endpoints = [
    ("/", secret_key, ["GET"], "secret_key"),
    ("/fixtures", secret_key, ["POST"], "fixtures"),
]


def register_default_endpoints(app: FastAPI):
    default_endpoints = [
        {"path": "/", "endpoint": secret_key, "methods": ["GET"], "name": "secret_key"},
        {
            "path": "/fixtures",
            "endpoint": secret_key,
            "methods": ["POST"],
            "name": "fixtures",
        },
    ]
    for endpoint in default_endpoints:
        app.router.add_api_route(**endpoint)
