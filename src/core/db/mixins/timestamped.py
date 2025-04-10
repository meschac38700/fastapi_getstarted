import datetime

from sqlalchemy import func, text
from sqlmodel import DateTime, Field


class TimestampedModelMixin:
    created_at: datetime.datetime | None = Field(
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
        }
    )
    updated_at: datetime.datetime | None = Field(
        default=None,
        sa_type=DateTime,
        sa_column_kwargs={"onupdate": func.now(), "nullable": True},
    )
