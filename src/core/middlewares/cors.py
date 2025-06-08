from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from settings import settings


def cors_middleware(app: FastAPI):
    """append CORS middleware to the fastapi app."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=settings.cors_allowed_methods,
        allow_headers=settings.cors_allowed_headers,
    )
