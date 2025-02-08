from pydantic import BaseModel

from apps.user.models import User

from ._base import UserBaseModel


class UserCreate(UserBaseModel):
    pass


class UserList(BaseModel):
    users: list[str]

    async def to_object_list(self):
        return await User.filter(User.username.in_(self.users))
