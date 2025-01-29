from sqlmodel import Field

from core.db import SQLTable
from core.db.models import TimestampedSQLBaseModel


class HeroBase(SQLTable):
    name: str = Field(index=True)
    secret_name: str
    age: int | None = None
    user_id: int | None = Field(default=None, foreign_key="user.id")


class HeroSQLBaseModel(HeroBase, TimestampedSQLBaseModel):
    pass
