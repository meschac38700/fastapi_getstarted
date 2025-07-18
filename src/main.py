from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.db.dependencies.session import get_engine
from core.db.signals.main import setup_signals
from core.lifespan import setup, teardown
from core.middlewares import cors_middleware
from core.monitoring.sentry import sentry_init
from core.routers import register_default_endpoints
from core.routers.register import AppRouter
from core.security.csrf import csrf_exception_handler
from core.services import celery

_engine = get_engine()


@asynccontextmanager
async def lifespan(_: FastAPI):
    sentry_init()
    setup_signals()
    await setup(_engine)
    yield
    await teardown(_engine)


app = FastAPI(lifespan=lifespan)
app.celery = celery

csrf_exception_handler(app)
cors_middleware(app)
register_default_endpoints(app)
# register routers from apps directory
AppRouter().register_all(app)
