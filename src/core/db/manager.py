import itertools
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql._typing import ColumnExpressionArgument
from sqlmodel import SQLModel, select

from settings import settings

Fn = Callable[..., Any]
T = TypeVar("T", bound=SQLModel)


def session_decorator(func: Fn) -> Fn:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        engine = settings.get_engine()
        async with AsyncSession(engine) as session:
            kwargs["session"] = session
            res = await func(*args, **kwargs)
            await engine.dispose()
        return res

    return wrapper


class ModelManager:
    """Group some utility functions for db queries."""

    def __init__(self, model_class: type[SQLModel]):
        super().__init__()
        self.model_class = model_class

    @session_decorator
    async def insert(self, data: dict[str, Any], session: AsyncSession):
        item = self.model_class(**data)
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return item

    @session_decorator
    async def insert_batch(
        self,
        data: list[SQLModel],
        *,
        batch_size: int = 50,
        session: AsyncSession = None,
    ):
        """Insert a batch of SQLModel instances."""
        batches = itertools.batched(data, batch_size)
        for batch in batches:
            session.add_all(batch)
            await session.commit()

    @session_decorator
    async def get(
        self, filter_by: ColumnExpressionArgument[bool] | bool, *, session: AsyncSession
    ):
        res = await session.scalars(select(self.model_class).where(filter_by))
        return res.first()

    @session_decorator
    async def all(
        self,
        *,
        session: AsyncSession = None,
        offset: int = 0,
        limit: int = 100,
    ):
        """Get all items of the given model."""

        # based on https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#dynamic-asyncio
        data = await session.scalars(
            select(self.model_class).offset(offset).limit(limit)
        )

        return data.all()

    @session_decorator
    async def filter(
        self,
        filters: ColumnExpressionArgument[bool] | bool,
        *,
        session: AsyncSession = None,
        offset: int = 0,
        limit: int = 100,
    ):
        data_list = await session.scalars(
            select(self.model_class).where(filters).offset(offset).limit(limit)
        )
        return data_list.all()

    @session_decorator
    async def exists(
        self,
        *,
        session: AsyncSession = None,
        filters: ColumnExpressionArgument[bool] | bool,
    ) -> bool:
        data_list = await session.scalars(select(self.model_class).where(filters))
        return data_list.first() is not None

    @session_decorator
    async def delete(self, item: SQLModel, *, session: AsyncSession):
        await session.delete(item)
        await session.commit()
