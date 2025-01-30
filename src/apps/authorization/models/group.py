from typing import Iterable

from sqlmodel import Field, Relationship

from apps.authorization.mixins import PermissionMixin
from apps.user.models import User

from ._base import GroupBase
from .permission import Permission
from .relation_links import GroupUserLink, PermissionGroupLink


class Group(PermissionMixin, GroupBase, table=True):
    id: int = Field(primary_key=True, allow_mutation=False)
    permissions: list[Permission] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}, link_model=PermissionGroupLink
    )
    users: list[User] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}, link_model=GroupUserLink
    )

    async def add_user(self, user: User):
        self.users.append(user)
        await self.save()

    async def extend_users(self, users: Iterable[User]):
        self.users.extend(users)
        await self.save()

    async def remove_users(self, users: Iterable[User]):
        self.users = [u for u in self.users if u not in users]
        await self.save()
