from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from settings import settings


def session_middleware(app: FastAPI):
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        session_cookie=settings.session_cookie,
        max_age=settings.max_age,
        https_only=settings.cookie_secure,
        same_site=settings.cookie_samesite,
        domain=settings.cookie_domain,
    )
