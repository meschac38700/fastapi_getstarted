from sqlmodel import Field

from core.db import SQLTable


class HeroBase(SQLTable):
    name: str = Field(index=True)
    secret_name: str
    age: int | None = None
