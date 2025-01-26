from sqlmodel import Field

from core.db import SQLTable


class PermissionUserLink(SQLTable, table=True):
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    permission_id: int | None = Field(
        default=None, foreign_key="permission.id", primary_key=True
    )


class PermissionGroupLink(SQLTable, table=True):
    group_id: int | None = Field(default=None, foreign_key="group.id", primary_key=True)
    permission_id: int | None = Field(
        default=None, foreign_key="permission.id", primary_key=True
    )


class GroupUserLink(SQLTable, table=True):
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    group_id: int | None = Field(default=None, foreign_key="group.id", primary_key=True)
