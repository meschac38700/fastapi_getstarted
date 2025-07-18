import re
from importlib import import_module
from typing import TYPE_CHECKING, Any, Iterable, Sequence

from sqlmodel import Relationship

from apps.authorization.models import (
    GroupUserLink,
    Permission,
    PermissionUserLink,
)
from core.auth.hashers import PasswordHasher
from core.db.mixins import BaseTable
from settings import settings

from ._base import UserBaseModel

if TYPE_CHECKING:
    from apps.authorization.models import Group
_EMPTY = type("Empty", (), {})


class User(UserBaseModel, BaseTable, table=True):
    __tablename__ = "users"

    permissions: list[Permission] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}, link_model=PermissionUserLink
    )
    groups: list["Group"] = Relationship(
        back_populates="users",
        sa_relationship_kwargs={"lazy": "joined"},
        link_model=GroupUserLink,
    )

    def model_post_init(self, __context: Any) -> None:
        self._hash_password()

    def has_permissions(
        self, permissions: Iterable[Permission], any_match: bool = False
    ) -> bool:
        if self.is_admin:
            return True
        return super().has_permissions(permissions, any_match)

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
        pkg, hasher_class_name = re.search(pattern, settings.password_hasher).groups()
        hasher_pkg = import_module(pkg)
        return getattr(hasher_pkg, hasher_class_name)

    def set_password(self, password_plain: str):
        self.password = password_plain
        self._hash_password(force=True)

    def _hash_password(self, force=False):
        if self.id is None or force:
            self.password = self._password_hasher.hash(self.password)

    def check_password(self, password_plain: str):
        return self._password_hasher.verify(password_plain, self.password)

    def _intersection_groups(self, groups: list["Group"]) -> list["Group"]:
        groups_belong_to = []
        user_groups = self.groups
        for group in groups:
            if group in user_groups:
                groups_belong_to.append(group)

        return groups_belong_to

    def _belongs_to_any_groups(
        self, groups: list["Group"]
    ) -> tuple[bool, list["Group"]]:
        if not self.groups:
            return False, groups

        belong_groups = self._intersection_groups(groups)
        return len(belong_groups) > 1, belong_groups

    def belongs_to_groups(
        self, groups: list["Group"] | Sequence["Group"], *, any_match: bool = False
    ) -> tuple[bool, list["Group"]]:
        if not self.groups:
            return False, groups

        if any_match:
            return self._belongs_to_any_groups(groups)

        belong_groups = self._intersection_groups(groups)
        return len(belong_groups) == len(groups), belong_groups

    async def add_to_groups(self, groups: Iterable["Group"]):
        missing_groups = [grp for grp in groups if grp not in self.groups]
        self.groups.extend(missing_groups)
        return await self.save()
