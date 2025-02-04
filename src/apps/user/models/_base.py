import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlmodel import Field

from apps.user.utils.types import UserRole
from core.db import SQLTable
from core.db.models import TimestampedSQLBaseModel


class UserBase(SQLTable):
    username: str = Field(unique=True, index=True)
    first_name: str
    last_name: str
    password: str
    email: str | None = Field(default=None, unique=True)
    address: str | None = None
    age: int | None = None


class UserSQLBaseModel(UserBase, TimestampedSQLBaseModel):
    role: UserRole = Field(
        sa_column=sa.Column(
            postgresql.ENUM(UserRole), default=UserRole.active, index=True
        )
    )
