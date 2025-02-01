from sqlmodel import Field

from core.db import SQLTable


class PermissionUserLink(SQLTable, table=True):
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    permission_name: str | None = Field(
        default=None, foreign_key="permission.name", primary_key=True
    )


class PermissionGroupLink(SQLTable, table=True):
    group_name: str | None = Field(
        default=None, foreign_key="permission_group.name", primary_key=True
    )
    permission_name: str | None = Field(
        default=None, foreign_key="permission.name", primary_key=True
    )


class GroupUserLink(SQLTable, table=True):
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    group_name: str | None = Field(
        default=None, foreign_key="permission_group.name", primary_key=True
    )
