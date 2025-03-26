from typing import Sequence

from pydantic import BaseModel

from apps.authorization.models import Permission
from apps.authorization.models._base import PermissionBase


class PermissionCreate(PermissionBase):
    class ConfigDict:
        from_attributes = True


class PermissionList(BaseModel):
    permissions: list[str]

    async def to_object_list(self) -> Sequence[Permission]:
        return await Permission.filter(name__in=self.permissions)
