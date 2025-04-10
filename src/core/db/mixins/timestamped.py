import datetime

from sqlalchemy import text
from sqlmodel import Field


class TimestampedModelMixin:
    created_at: datetime.datetime | None = Field(
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
        }
    )
