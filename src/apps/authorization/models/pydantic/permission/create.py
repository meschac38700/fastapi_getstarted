from typing import Sequence

from pydantic import BaseModel

from apps.authorization.models._base import PermissionBase
from apps.authorization.models.permission import Permission


class PermissionCreate(PermissionBase):
    class ConfigDict:
        from_attributes = True


class PermissionList(BaseModel):
    permissions: list[str]

    async def to_object_list(self) -> Sequence[Permission]:
        return await Permission.filter(Permission.name.in_(self.permissions))
