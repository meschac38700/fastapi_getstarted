from apps.authorization.models._base import GroupBase
from core.db.utils import optional_fields


@optional_fields
class GroupUpdate(GroupBase):
    class ConfigDict:
        from_attributes = True
