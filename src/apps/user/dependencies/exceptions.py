from fastapi import FastAPI, Request, status
from starlette.responses import RedirectResponse

from settings import settings


class AccessDeniedError(Exception):
    def __init__(
        self,
        status_code: int = status.HTTP_307_TEMPORARY_REDIRECT,
        location: str | None = None,
    ):
        self.status_code = status_code
        self.location = location or settings.session_auth_redirect_success


def access_denied_exception_handler(app: FastAPI):
    """Global exception handler for AccessDeniedError."""

    @app.exception_handler(AccessDeniedError)
    def redirect_exception_handler(_: Request, exc: AccessDeniedError):
        return RedirectResponse(url=exc.location, status_code=exc.status_code)
