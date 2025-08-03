import re
from typing import Any, Callable, ParamSpec

from fastapi import FastAPI, Request, Response
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse

from core.auth.backend import AuthBackend
from settings import settings

P = ParamSpec("P")
Fn = Callable[P, Any]


class SessionAuthRequiredMiddleware(BaseHTTPMiddleware):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exempt_paths = settings.EXEMPT_AUTH_URLS

    def is_exempt_path(self, url_path: str):
        return any(
            re.search(re.compile("^" + pattern), url_path) is not None
            for pattern in self.exempt_paths
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        current_path = request.url.path

        # Skip exempt paths
        if self.is_exempt_path(current_path):
            return await call_next(request)

        if request.url.path.startswith(settings.WEB_ROUTER_PREFIX):
            # Template view only: Check session auth
            session_user = (
                request.session.get(settings.session_user_key)
                if hasattr(request, "session")
                else None
            )
            if not session_user:
                return RedirectResponse(url=settings.SESSION_AUTH_URL)

        return await call_next(request)


def auth_related_middlewares(app: FastAPI):
    app.add_middleware(SessionAuthRequiredMiddleware)
    app.add_middleware(AuthenticationMiddleware, backend=AuthBackend())
