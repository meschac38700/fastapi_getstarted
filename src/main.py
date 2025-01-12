import secrets
from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.db.fixtures import LoadFixtures
from core.lifespan import setup, teardown
from core.routers.register import AppRouter
from settings import settings

_engine = settings.get_engine()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await setup(_engine)
    yield
    await teardown(_engine)


app = FastAPI(lifespan=lifespan)
AppRouter().register_all(app)


@app.get("/", name="Generate secret key.")
def secret_key(length: int = 65):
    secret = secrets.token_urlsafe(length)
    return {"secret": secret}


@app.post("/fixtures", name="Load app initial data.")
async def load_fake_data():
    await LoadFixtures().load_fixtures()
    return {"Loaded": True}
