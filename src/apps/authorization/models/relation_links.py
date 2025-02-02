from sqlmodel import Field

from core.db import SQLTable


class PermissionUserLink(SQLTable, table=True):
    user_id: int | None = Field(
        default=None, foreign_key="user.id", primary_key=True, ondelete="CASCADE"
    )
    permission_name: str | None = Field(
        default=None,
        foreign_key="permission.name",
        primary_key=True,
        ondelete="CASCADE",
    )


class PermissionGroupLink(SQLTable, table=True):
    group_name: str | None = Field(
        default=None,
        foreign_key="permission_group.name",
        primary_key=True,
        ondelete="CASCADE",
    )
    permission_name: str | None = Field(
        default=None,
        foreign_key="permission.name",
        primary_key=True,
        ondelete="CASCADE",
    )


class GroupUserLink(SQLTable, table=True):
    user_id: int | None = Field(
        default=None, foreign_key="user.id", primary_key=True, ondelete="CASCADE"
    )
    group_name: str | None = Field(
        default=None,
        foreign_key="permission_group.name",
        primary_key=True,
        ondelete="CASCADE",
    )
