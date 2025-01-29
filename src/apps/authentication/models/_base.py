from sqlmodel import Field

from core.db import SQLTable
from core.db.models import TimestampedSQLBaseModel


class JWTTokenBase(SQLTable):
    access_token: str
    token_type: str = Field(default="Bearer")


class JWTTokenSQLBaseModel(JWTTokenBase, TimestampedSQLBaseModel):
    pass
