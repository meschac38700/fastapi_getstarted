from functools import wraps
from typing import Callable, ParamSpec

from fastapi_csrf_protect import CsrfProtect
from starlette.responses import HTMLResponse

from settings.csrf import CSRFSettings

P = ParamSpec("P")
Fn = Callable[P, HTMLResponse]


def csrf_protect(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> HTMLResponse:
        CsrfProtect.load_config(CSRFSettings)
        response = func(*args, **kwargs)
        return response

    return wrapper
