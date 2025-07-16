from sqlmodel import Relationship

from apps.user.models import User
from core.db.mixins import BaseTable

from ._base import HeroBase


class Hero(HeroBase, BaseTable, table=True):
    user: User = Relationship(sa_relationship_kwargs={"lazy": "joined"})
