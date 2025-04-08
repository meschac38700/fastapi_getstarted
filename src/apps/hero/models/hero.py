from sqlmodel import Field, Relationship

from apps.user.models import User

from ._base import HeroModel


class Hero(HeroModel, table=True):
    id: int | None = Field(default=None, primary_key=True, allow_mutation=False)
    user: User = Relationship(sa_relationship_kwargs={"lazy": "joined"})
