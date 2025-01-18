from .._base import UserBase


class UserBaseModel(UserBase):
    class ConfigDict:
        from_attributes = True
