import re
from typing import Any, Callable, ParamSpec

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse

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

        application_json = "application/json" in request.headers.get("Accept")
        # Skip if it's test environment and not requesting for an HTML response
        if application_json:
            return await call_next(request)

        # Skip Ajax/API requests
        if (
            application_json
            or request.headers.get("x-requested-with") == "XMLHttpRequest"
        ):
            return await call_next(request)

        # Skip requests with JWT (Authorization: Bearer)
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return await call_next(request)

        # Template view only: Check session auth
        session_user = (
            request.session.get(settings.session_user_key)
            if hasattr(request, "session")
            else None
        )
        if not session_user:
            return RedirectResponse(url=settings.SESSION_AUTH_URL)

        return await call_next(request)


def session_login_required(app: FastAPI):
    app.add_middleware(SessionAuthRequiredMiddleware)
