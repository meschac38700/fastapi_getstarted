from sqlmodel import Field, Relationship

from apps.authorization.mixins import PermissionMixin
from apps.user.models import User

from ._base import GroupBase
from .permission import Permission


class Group(PermissionMixin, GroupBase, table=True):
    id: int = Field(primary_key=True, allow_mutation=False)
    users: list[User] = Relationship(sa_relationship_kwargs={"lazy": "joined"})
    permissions: list[Permission] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}
    )
