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
