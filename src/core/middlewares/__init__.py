from fastapi import FastAPI
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from .auth import auth_related_middlewares
from .cors import cors_middleware
from .session import session_middleware


def register_middlewares(app: FastAPI):
    cors_middleware(app)
    auth_related_middlewares(app)
    session_middleware(app)
    app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])


__all__ = ["register_middlewares"]
