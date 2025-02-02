from sqlmodel import Field

from core.db import SQLTable


class PermissionBase(SQLTable):
    name: str = Field(unique=True)
    target_table: str = Field(index=True)
    display_name: str | None
    description: str | None


class GroupBase(SQLTable):
    name: str = Field(unique=True)
    target_table: str = Field(index=True)
    display_name: str | None
    description: str | None
