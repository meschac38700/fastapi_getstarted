from apps.authorization.models._base import PermissionBase
from core.models.utils import optional_fields


@optional_fields
class PermissionUpdate(PermissionBase):
    class ConfigDict:
        from_attributes = True
