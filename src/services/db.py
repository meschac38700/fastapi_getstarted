from collections.abc import Callable
from functools import lru_cache, wraps
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql._typing import ColumnExpressionArgument
from sqlmodel import SQLModel, select

from settings import settings

Fn = Callable[..., Any]


def session_decorator(func: Fn) -> Fn:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        self_obj = args[0]
        async with AsyncSession(self_obj.engine) as session:
            kwargs["session"] = session
            res = await func(*args, **kwargs)
        return res

    return wrapper


class DBService:
    """Group some utility functions for db queries."""

    def __init__(self):
        self.engine = settings.get_engine()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.dispose()

    async def dispose(self):
        await self.engine.dispose()

    @session_decorator
    async def insert_batch(
        self, instances: list[SQLModel], *, session: AsyncSession = None
    ):
        """Insert a batch of SQLModel instances."""
        session.add_all(instances)
        await session.commit()

    @session_decorator
    async def all(
        self,
        model: SQLModel,
        *,
        session: AsyncSession = None,
        offset: int = 0,
        limit: int = 100,
    ):
        """Get all items of the given model."""

        # based on https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#dynamic-asyncio
        data = await session.scalars(select(model).offset(offset).limit(limit))

        return data.all()

    @session_decorator
    async def filter(
        self,
        model: SQLModel,
        filters: ColumnExpressionArgument[bool] | bool,
        *,
        session: AsyncSession = None,
        offset: int = 0,
        limit: int = 100,
    ):
        data_list = await session.scalars(
            select(model).where(filters).offset(offset).limit(limit)
        )
        return data_list.all()

    @session_decorator
    async def exists(
        self,
        model: SQLModel,
        *,
        session: AsyncSession = None,
        filters: ColumnExpressionArgument[bool] | bool,
    ) -> bool:
        data_list = await session.scalars(select(model).where(filters))
        return data_list.first() is not None

    # TODO(Complete with others functions)


@lru_cache
def get_db_service():
    return DBService()
