import datetime

from sqlalchemy import func, text
from sqlmodel import DateTime, Field, SQLModel


class IDModel(SQLModel):
    id: int = Field(default=None, primary_key=True, allow_mutation=False)


class TimestampedModel(SQLModel):
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


class BaseTable(TimestampedModel, IDModel):
    """Include default fields like: ID, created_at, updated_at."""
