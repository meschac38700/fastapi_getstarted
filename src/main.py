from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from core.db.dependencies.session import get_engine
from core.db.signals.main import setup_signals
from core.lifespan import setup, teardown
from core.middlewares import cors_middleware
from core.monitoring.sentry import sentry_init
from core.routers import register_default_endpoints
from core.routers.register import AppRouter
from core.security.csrf import csrf_exception_handler
from core.services import celery
from core.services.files import apps as file_apps
from settings import settings

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
static_packages = file_apps.static_packages()
app.mount(
    settings.STATIC_URL,
    StaticFiles(
        check_dir=False, packages=static_packages, directory=settings.STATIC_ROOT
    ),
    name="static",
)

csrf_exception_handler(app)
cors_middleware(app)
register_default_endpoints(app)
# register routers from apps directory
AppRouter().register_all(app)
