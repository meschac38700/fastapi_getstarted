from typing import TYPE_CHECKING, Iterable

from sqlmodel import Relationship

from core.db.mixins import BaseTable

from ._base import GroupBase
from .mixins import CRUDModelMixin, PermissionMixin
from .permission import Permission
from .relation_links import GroupUserLink, PermissionGroupLink

if TYPE_CHECKING:
    from apps.user.models import User


class Group(CRUDModelMixin, BaseTable, PermissionMixin, GroupBase, table=True):
    __tablename__ = "permission_group"

    permissions: list[Permission] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}, link_model=PermissionGroupLink
    )
    users: list["User"] = Relationship(
        back_populates="groups",
        sa_relationship_kwargs={"lazy": "joined"},
        link_model=GroupUserLink,
    )

    async def add_user(self, user: "User"):
        self.users.append(user)
        await self.save()

    async def extend_users(self, users: Iterable["User"]):
        self.users.extend([user for user in users if user not in self.users])
        await self.save()

    async def remove_users(self, users: Iterable["User"]):
        self.users = [u for u in self.users if u not in users]
        await self.save()
