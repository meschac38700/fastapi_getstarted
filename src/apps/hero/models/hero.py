from sqlmodel import Field, Relationship

from apps.user.models import User

from ._base import HeroBase


class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True, allow_mutation=False)
    user: User = Relationship(sa_relationship_kwargs={"lazy": "joined"})
