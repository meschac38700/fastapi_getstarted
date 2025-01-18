import re
from importlib import import_module
from typing import Any

from sqlmodel import Field

from core.auth.hashers import PasswordHasher
from settings import PASSWORD_HASHER

from ._base import UserBase

_EMPTY = type("Empty", (), {})


class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True, allow_mutation=False)

    def model_post_init(self, __context: Any) -> None:
        self._hash_password()

    def update_from_dict(self, data: dict[str, Any]):
        for key, value in data.items():
            self_val = getattr(self, key, _EMPTY)
            if self_val is not _EMPTY:
                setattr(self, key, value)

        if "password" in data:
            self._hash_password(force=True)

    @property
    def _password_hasher(self) -> PasswordHasher:
        pattern = r"^(?P<pkg>.+)\.(?P<hasher_class>\w+)$"
        pkg, hasher_class_name = re.search(pattern, PASSWORD_HASHER).groups()
        hasher_pkg = import_module(pkg)
        return getattr(hasher_pkg, hasher_class_name)

    def set_password(self, password_plain: str):
        self.password = password_plain
        self._hash_password(force=True)

    def _hash_password(self, force=False):
        if self.id is None or force:
            self.password = self._password_hasher.hash(self.password)

    def check_password(self, password_plain: str):
        print(f"Verify: {password_plain=}, {self.password=}")
        return self._password_hasher.verify(password_plain, self.password)
