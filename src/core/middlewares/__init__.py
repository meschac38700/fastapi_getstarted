from fastapi import FastAPI

from .auth import auth_related_middlewares
from .cors import cors_middleware
from .session import session_middleware


def register_middlewares(app: FastAPI):
    cors_middleware(app)
    auth_related_middlewares(app)
    session_middleware(app)


__all__ = ["register_middlewares"]
