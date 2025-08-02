import hashlib

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlmodel import Field

from apps.authorization.models.mixins import PermissionMixin
from apps.user.utils.types import UserRole, UserStatus
from core.db import SQLTable
from core.db.mixins import BaseTable
from core.db.models import AuthUser


class UserBase(SQLTable):
    username: str = Field(unique=True, index=True)
    first_name: str
    last_name: str
    password: str
    email: str | None = Field(default=None, unique=True)
    address: str | None = None
    age: int | None = None


class UserBaseModel(PermissionMixin, BaseTable, UserBase, AuthUser):
    role: UserRole = Field(
        default=UserRole.active,
        sa_column=sa.Column(
            postgresql.ENUM(UserRole, name="role"), default=UserRole.active, index=True
        ),
    )
    status: UserStatus = Field(
        default=UserStatus.inactive,
        sa_column=sa.Column(
            postgresql.ENUM(UserStatus, name="status"),
            default=UserStatus.inactive,
            index=True,
        ),
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def email_hash(self):
        return hashlib.sha256((self.email or self.username).encode("utf-8")).hexdigest()

    @property
    def avatar_url(self) -> str:
        return f"https://0.gravatar.com/avatar/{self.email_hash}"

    @property
    def is_admin(self) -> bool:
        return self.role is UserRole.admin

    @property
    def is_staff(self) -> bool:
        return self.role is UserRole.staff

    @property
    def is_active(self) -> bool:
        return self.role is UserRole.active
