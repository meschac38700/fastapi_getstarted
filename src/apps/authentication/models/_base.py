from sqlmodel import Field

from core.db import SQLTable
from core.db.models import TimestampedModelMixin


class JWTTokenBase(SQLTable):
    access_token: str
    token_type: str = Field(default="Bearer")


class JWTTokenModelMixin(JWTTokenBase, TimestampedModelMixin):
    pass
