from sqlmodel import Field

from core.db import SQLTable


class JWTTokenBase(SQLTable):
    access_token: str
    token_type: str = Field(default="bearer")
