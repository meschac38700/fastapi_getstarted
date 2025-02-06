from apps.authorization.models._base import GroupBase
from core.models.utils import optional_fields


@optional_fields
class GroupUpdate(GroupBase):
    class ConfigDict:
        from_attributes = True
