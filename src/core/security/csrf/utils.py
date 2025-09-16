from functools import lru_cache
from typing import Awaitable, Callable, ParamSpec

from fastapi import FastAPI, Request, Response
from fastapi_csrf_protect.exceptions import CsrfProtectError
from fastapi_csrf_protect.flexible import CsrfProtect
from fastapi_csrf_protect.load_config import LoadConfig
from starlette.responses import HTMLResponse

from settings.csrf import CSRFSettings

P = ParamSpec("P")
Fn = Callable[P, Awaitable[HTMLResponse]]


@lru_cache
def get_csrf_protect():
    def _only_csrf_fields():
        _settings = CSRFSettings()
        config_fields = LoadConfig.model_fields.keys()
        return list(_settings.model_dump(include=config_fields).items())

    CsrfProtect.load_config(_only_csrf_fields)
    return CsrfProtect()


async def csrf_required(request: Request, response: Response):
    """Validate CSRF token."""
    csrf_protect = get_csrf_protect()
    await csrf_protect.validate_csrf(request)
    csrf_protect.unset_csrf_cookie(response)  # prevent token reuse


def csrf_exception_handler(app: FastAPI):
    @app.exception_handler(CsrfProtectError)
    def csrf_protect_exception_handler(_: Request, exc: CsrfProtectError):
        return HTMLResponse(exc.message, status_code=exc.status_code)
