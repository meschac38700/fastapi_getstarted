import re
from functools import lru_cache
from importlib import import_module

from pydantic import field_validator
from sqlmodel import Field

from core.auth.hashers import PasswordHasher
from settings import PASSWORD_HASHER

from ._base import UserBase


class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True, allow_mutation=False)

    @field_validator("password", mode="before")
    @classmethod
    def password_hash(cls, value: str) -> str:
        # Bug: https://github.com/fastapi/sqlmodel/pull/1041/files
        _value = cls._password_hasher().hash(value)
        return _value

    @classmethod
    @lru_cache
    def _password_hasher(cls) -> PasswordHasher:
        pattern = r"^(?P<pkg>.+)\.(?P<hasher_class>\w+)$"
        pkg, hasher_class_name = re.search(pattern, PASSWORD_HASHER).groups()
        hasher_pkg = import_module(pkg)
        return getattr(hasher_pkg, hasher_class_name)

    def check_password(self, password_plain: str):
        return self._password_hasher().verify(password_plain, self.password)
