from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.lifespan import setup, teardown
from core.routers import register_default_endpoints
from core.routers.register import AppRouter
from settings import settings

_engine = settings.get_engine()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await setup(_engine)
    yield
    await teardown(_engine)


app = FastAPI(lifespan=lifespan)
register_default_endpoints(app)
# register routers from apps directory
AppRouter().register_all(app)
