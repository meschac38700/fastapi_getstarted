from sqlmodel import Field

from core.db import SQLTable


class UserBase(SQLTable):
    username: str = Field(unique=True, index=True)
    first_name: str
    last_name: str
    # TODO(Eliam): Add password field
    email: str | None = Field(default=None, unique=True)
    address: str | None = None
    age: int | None = None
