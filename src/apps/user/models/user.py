from sqlmodel import Field

from ._base import UserBase


class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True, allow_mutation=False)
