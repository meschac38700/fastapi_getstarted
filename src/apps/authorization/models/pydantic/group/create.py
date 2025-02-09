from apps.authorization.models._base import GroupBase


class GroupCreate(GroupBase):
    class ConfigDict:
        from_attributes = True
