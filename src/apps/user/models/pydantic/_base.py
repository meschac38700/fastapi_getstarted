from .._base import UserBase


class UserBaseModel(UserBase):
    class Config:
        from_attributes = True
