from sqlmodel import SQLModel

from .hero.models import Hero  # noqa: F403, F401
from .user.models import User  # noqa: F403, F401

app_metadata = [
    SQLModel.metadata,
]

__all__ = [
    "app_metadata",
]
