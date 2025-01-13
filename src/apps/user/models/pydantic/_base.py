from .._base import UserBase


class UserBaseModel(UserBase):
    class Config:
        orm_mode = False
