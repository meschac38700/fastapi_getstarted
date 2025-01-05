import secrets
from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.lifespan import setup, teardown
from routers import register_app_routers
from settings import db_settings

_engine = db_settings.get_engine()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await setup(_engine)
    yield
    await teardown(_engine)


app = FastAPI(lifespan=lifespan)
register_app_routers(app)


@app.get("/", name="Generate secret key.")
def secret_key(length: int = 65):
    secret = secrets.token_urlsafe(length)
    return {"secret": secret}
