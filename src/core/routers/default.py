import secrets

from celery import states as celery_states
from fastapi import FastAPI, HTTPException, status
from starlette.responses import RedirectResponse

from apps.user.models import User
from core.monitoring.logger import get_logger
from core.tasks import liveness_task, load_fixtures_task
from core.tasks.exceptions import SQLAlchemyIntegrityError
from redis import asyncio as aioredis
from settings import settings

_logger = get_logger(__name__)


async def health_check(liveness: bool = False, readiness: bool = False):
    """Check the health of the application.

    @param liveness: Whether the application is functional.
    @param readines: Whether the application and its dependencies are functional.
    """

    test_result = {"status": "KO"}

    if liveness:
        test_result["status"] = "OK"
        return test_result

    if readiness:
        # check that the database is up
        await User.count()
        # check that redis is up
        redis = aioredis.from_url(settings.celery_broker)
        await redis.ping()
        # check that celery is responding
        assert liveness_task.delay().get()

        test_result["status"] = "OK"
        return test_result

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=test_result
    )


def permanent_redirect():
    """Redirect user to the page after login succeed."""
    return RedirectResponse(
        settings.session_auth_redirect_success,
        status_code=status.HTTP_308_PERMANENT_REDIRECT,
    )


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
        if isinstance(e, SQLAlchemyIntegrityError):
            response["status"] = celery_states.REJECTED
            response["msg"] = "Fixtures already loaded."
            _logger.debug("IntegrityError during load fixtures task.", exc_info=e)
        else:
            _logger.debug("An error occurred during load fixtures task.", exc_info=e)

    return response


def register_default_endpoints(app: FastAPI):
    default_tags = ["Default"]

    default_endpoints = [
        {
            "path": "/",
            "endpoint": permanent_redirect,
            "methods": ["GET"],
            "name": "redirect",
            "tags": default_tags,
        },
        {
            "path": "/default/",
            "endpoint": secret_key,
            "methods": ["GET"],
            "name": "secret-key",
            "tags": default_tags,
        },
        {
            "path": "/default/healthcheck/",
            "endpoint": health_check,
            "methods": ["GET"],
            "name": "health-check",
            "tags": default_tags,
        },
        {
            "path": "/default/fixtures/",
            "endpoint": load_fixtures,
            "methods": ["POST"],
            "name": "load-fixtures",
            "tags": default_tags,
        },
    ]
    for endpoint in default_endpoints:
        app.router.add_api_route(**endpoint)
