from collections.abc import Callable
from functools import wraps
from typing import Annotated, Any, TypeVar

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql._typing import ColumnExpressionArgument
from sqlmodel import select

from core.db import SQLTable
from settings import settings

Fn = Callable[..., Any]
T = TypeVar("T", bound=SQLTable)


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
    async def insert(self, item: T, *, session: AsyncSession):
        session.add(item)
        await session.commit()
        await session.refresh(item)

    @session_decorator
    async def insert_batch(
        self, instances: list[SQLTable], *, session: AsyncSession = None
    ):
        """Insert a batch of SQLTable instances."""
        session.add_all(instances)
        await session.commit()

    @session_decorator
    async def get(
        self,
        model: SQLTable,
        filter_by: ColumnExpressionArgument[bool] | bool,
        *,
        session: AsyncSession,
    ):
        res = await session.scalars(select(model).where(filter_by))
        return res.first()

    @session_decorator
    async def all(
        self,
        model: SQLTable,
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
        model: SQLTable,
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
        model: SQLTable,
        *,
        session: AsyncSession = None,
        filters: ColumnExpressionArgument[bool] | bool,
    ) -> bool:
        data_list = await session.scalars(select(model).where(filters))
        return data_list.first() is not None

    @session_decorator
    async def refresh(self, instance: SQLTable, *args, session: AsyncSession, **kwargs):
        await session.refresh(instance, *args, **kwargs)
        return instance

    @session_decorator
    async def delete(self, instance: SQLTable, *, session: AsyncSession):
        await session.delete(instance)
        await session.commit()

    # TODO(Complete with others functions)


async def get_db_service():
    async with DBService() as db:
        yield db


DBServiceDep = Annotated[DBService, Depends(get_db_service)]