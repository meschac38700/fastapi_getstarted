from sqlmodel import SQLModel

from .authentication.models import JWTToken  # noqa: F403, F401
from .authorization.models.group import Group  # noqa: F403, F401
from .authorization.models.permission import Permission  # noqa: F403, F401
from .hero.models import Hero  # noqa: F403, F401
from .user.models import User  # noqa: F403, F401

app_metadata = [
    SQLModel.metadata,
]

__all__ = [
    "app_metadata",
]
