import asyncio
from collections.abc import Callable
from functools import wraps
from typing import Iterable

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlmodel import SQLModel, delete, select
from typing_extensions import Annotated, Any, ParamSpec, TypeVar

from settings import settings

P = ParamSpec("P")
Fn = Callable[P, Any]
T = TypeVar("T", bound=SQLModel)


def flush_session(func: Fn) -> Fn:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        self_obj = args[0]
        res = await func(*args, **kwargs)
        await self_obj.session.flush()
        return res

    return wrapper


class DBService:
    """Group some utility functions for db queries."""

    def __init__(self, engine: AsyncEngine = None):
        self.engine = engine or settings.get_engine()
        self._session: AsyncSession | None = None

    @property
    def session(self) -> AsyncSession:
        if self._session is not None and self._session.is_active:
            return self._session

        self._session = AsyncSession(self.engine)
        return self._session

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.dispose()

    async def dispose(self):
        await self.engine.dispose()

    @flush_session
    async def insert(self, item: T):
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    @flush_session
    async def insert_batch(
        self,
        instances: list[SQLModel],
    ):
        """Insert a batch of SQLModel instances."""
        async with self.session.begin_nested():
            self.session.add_all(instances)
        await self.session.commit()

    @flush_session
    async def get(self, model: SQLModel, **filters):
        filter_by = model.resolve_filters(**filters)
        res = await self.session.scalars(select(model).where(*filter_by))
        return res.first()

    @flush_session
    async def values(self, model: SQLModel, *attrs, **kwargs):
        session = kwargs.get("session")
        filters = kwargs.get("filters", {})

        _values = [model.get_attribute(attr) for attr in attrs]
        if filters:
            filter_by = model.resolve_filters(**filters)
            res = await session.execute(select(*_values).where(*filter_by))
        else:
            res = await session.execute(select(*_values))

        return res.all()

    @flush_session
    async def all(
        self,
        model: SQLModel,
        *,
        offset: int = 0,
        limit: int = 100,
    ):
        """Get all items of the given model."""

        # based on https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#dynamic-asyncio
        data = await self.session.scalars(select(model).offset(offset).limit(limit))

        return data.unique().all()

    @flush_session
    async def filter(
        self,
        model: SQLModel,
        *,
        offset: int = 0,
        limit: int = 100,
        **filters,
    ):
        filter_by = model.resolve_filters(**filters)
        data_list = await self.session.scalars(
            select(model).where(*filter_by).offset(offset).limit(limit)
        )
        return data_list.unique().all()

    @flush_session
    async def exists(
        self,
        model: SQLModel,
        instance: SQLModel,
    ) -> bool:
        filter_by = model.resolve_filters(id=instance.id)
        data_list = await self.session.scalars(select(model).where(*filter_by))
        return data_list.first() is not None

    @flush_session
    async def refresh(self, instance: SQLModel, *args, **kwargs) -> SQLModel:
        self.session.add(instance)
        await self.session.refresh(instance, *args, **kwargs)
        return instance

    @flush_session
    async def delete(self, instance: SQLModel):
        self.session.add(instance)
        await self.session.delete(instance)
        await self.session.commit()

    @flush_session
    async def bulk_delete(
        self,
        instances: Iterable[SQLModel],
    ):
        """Delete all given instances.

        Docs: https://docs.sqlalchemy.org/en/20/orm/session_basics.html#deleting"""
        async with self.session.begin_nested():
            await asyncio.gather(
                *[self.session.delete(instance) for instance in instances]
            )
        await self.session.commit()

    @flush_session
    async def truncate(self, instance: SQLModel):
        await self.session.execute(delete(instance))
        await self.session.commit()


async def get_db_service():
    async with DBService() as db:
        yield db


DBServiceDep = Annotated[DBService, Depends(get_db_service)]
