from sqlmodel import Field

from core.db import SQLTable
from core.db.mixins import TimestampedModelMixin


class JWTTokenBase(SQLTable):
    access_token: str
    token_type: str = Field(default="Bearer")


class JWTTokenModel(JWTTokenBase, TimestampedModelMixin):
    pass
