from sqlmodel import Field

from core.db import SQLTable
from core.db.mixins import BaseTable


class JWTTokenBase(SQLTable):
    access_token: str
    token_type: str = Field(default="Bearer")


class JWTTokenModel(BaseTable, JWTTokenBase):
    pass
