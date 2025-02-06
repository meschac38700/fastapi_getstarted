from apps.authorization.models._base import PermissionBase


class PermissionCreate(PermissionBase):
    class ConfigDict:
        from_attributes = True
