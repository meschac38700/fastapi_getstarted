import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlmodel import Field

from apps.user.utils.types import UserRole, UserStatus
from core.db import SQLTable
from core.db.mixins import TimestampedModelMixin


class UserBase(SQLTable):
    username: str = Field(unique=True, index=True)
    first_name: str
    last_name: str
    password: str
    email: str | None = Field(default=None, unique=True)
    address: str | None = None
    age: int | None = None


class UserBaseModel(UserBase, TimestampedModelMixin):
    role: UserRole = Field(
        default=UserRole.active,
        sa_column=sa.Column(
            postgresql.ENUM(UserRole, name="role"), default=UserRole.active, index=True
        ),
    )
    status: UserStatus = Field(
        default=UserStatus.inactive,
        sa_column=sa.Column(
            postgresql.ENUM(UserStatus, name="Status"),
            default=UserStatus.inactive,
            index=True,
        ),
    )

    @property
    def is_admin(self) -> bool:
        return self.role is UserRole.admin

    @property
    def is_staff(self) -> bool:
        return self.role is UserRole.staff

    @property
    def is_active(self) -> bool:
        return self.role is UserRole.active
