import re
from importlib import import_module
from typing import Any

from sqlmodel import Field

from core.auth.hashers import PasswordHasher
from core.db import SQLTable
from settings import PASSWORD_HASHER


class UserBase(SQLTable):
    username: str = Field(unique=True, index=True)
    first_name: str
    last_name: str
    password: str
    email: str | None = Field(default=None, unique=True)
    address: str | None = None
    age: int | None = None
    _password_hasher: PasswordHasher = None

    def model_post_init(self, __context: Any) -> None:
        self._hash_password()

    def _hash_password(self):
        pattern = r"^(?P<pkg>.+)\.(?P<hasher_class>\w+)$"
        pkg, hasher_class_name = re.search(pattern, PASSWORD_HASHER).groups()
        hasher_pkg = import_module(pkg)
        hasher_class = getattr(hasher_pkg, hasher_class_name)
        self._password_hasher = hasher_class()
        self.password = self._password_hasher.hash(self.password)

    def check_password(self, password_plain: str):
        return self._password_hasher.verify(password_plain, self.password)
