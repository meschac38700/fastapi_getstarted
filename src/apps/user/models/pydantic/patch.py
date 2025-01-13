from core.models.utils import optional_fields

from ._base import UserBaseModel


@optional_fields
class UserPatch(UserBaseModel):
    pass
