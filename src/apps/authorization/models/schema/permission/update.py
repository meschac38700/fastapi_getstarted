from apps.authorization.models._base import PermissionBase
from core.db.utils import optional_fields


@optional_fields
class PermissionUpdate(PermissionBase):
    class ConfigDict:
        from_attributes = True
