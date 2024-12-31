import datetime
from typing import TypeAlias

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseAsyncModel

DT: TypeAlias = Mapped[datetime.datetime]


class Item(BaseAsyncModel):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    create_at: DT = mapped_column(server_default=func.now())
