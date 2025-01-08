from sqlmodel import Field

from ._base import HeroBase


class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True, allow_mutation=False)
