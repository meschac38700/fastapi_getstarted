import asyncio
from collections.abc import Callable
from functools import wraps
from typing import Iterable

from fastapi import Depends
from sqlalchemy import func
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import ForUpdateArg
from sqlmodel import SQLModel, delete, select
from typing_extensions import Annotated, Any, ParamSpec, TypeVar

from core.db.dependencies.session import get_engine
from core.db.query.exceptions import ObjectNotFoundError

P = ParamSpec("P")
Fn = Callable[P, Any]
T = TypeVar("T", bound=SQLModel)


def inject_session(func: Fn) -> Fn:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        self_obj = args[0]
        _engine = get_engine()
        setattr(self_obj, "engine", _engine)
        async with AsyncSession(_engine) as session:
            kwargs["session"] = session
            setattr(self_obj, "_current_session", session)
            res = await func(*args, **kwargs)
            session.expunge_all()
        setattr(self_obj, "_current_session", None)
        return res

    return wrapper


class DBService:
    """Group some utility functions for db queries."""

    def __init__(self):
        self.engine = None
        self._current_session: AsyncSession | None = None

    @property
    def session(self) -> AsyncSession:
        if self._current_session is None:
            self._current_session = AsyncSession(self.engine)

        return self._current_session

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.dispose()

    async def dispose(self):
        await self.engine.dispose()

    @inject_session
    async def insert(self, item: T, *, session: AsyncSession = None):
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return item

    @inject_session
    async def bulk_create_or_update(
        self,
        instances: list[SQLModel],
        *,
        session: AsyncSession = None,
    ):
        """Insert a batch of SQLModel instances."""
        async with session.begin_nested():
            session.add_all(instances)
        await session.commit()

    @inject_session
    async def get(self, model: SQLModel, *, session: AsyncSession = None, **filters):
        filter_by = model.resolve_filters(**filters)
        res = await session.scalars(select(model).where(*filter_by))
        return res.first()

    @inject_session
    async def get_or_404(
        self, model: SQLModel, *, session: AsyncSession = None, **filters
    ):
        item = await self.get(model, session=session, **filters)
        if item is None:
            raise ObjectNotFoundError(f"Object {model.__name__} not found.")
        return item

    @inject_session
    async def first(self, model: SQLModel, *, session: AsyncSession = None):
        res = await session.scalars(select(model).limit(1))
        return res.first()

    @inject_session
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

    @inject_session
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

        return data.unique().all()

    @inject_session
    async def filter(
        self,
        model: SQLModel,
        *,
        session: AsyncSession = None,
        offset: int = 0,
        limit: int = 100,
        **filters,
    ):
        filter_by = model.resolve_filters(**filters)
        data_list = await session.scalars(
            select(model).where(*filter_by).offset(offset).limit(limit)
        )
        return data_list.unique().all()

    @inject_session
    async def count(
        self,
        model: SQLModel,
        *,
        session: AsyncSession = None,
        **filters,
    ) -> int:
        filter_by = model.resolve_filters(**filters)
        result = await session.scalars(select(func.count(model.id)).where(*filter_by))
        return result.unique().one()

    @inject_session
    async def exists(
        self,
        model: SQLModel,
        instance: SQLModel,
        *,
        session: AsyncSession = None,
    ) -> bool:
        filter_by = model.resolve_filters(id=instance.id)
        data_list = await session.scalars(select(model).where(*filter_by))
        return data_list.first() is not None

    @inject_session
    async def refresh(
        self,
        instance: SQLModel,
        *,
        session: AsyncSession,
        attribute_names: Iterable[str] | None = None,
        with_for_update: ForUpdateArg | None | bool | dict[str, Any] = None,
    ) -> SQLModel:
        session.add(instance)
        await session.refresh(
            instance, attribute_names=attribute_names, with_for_update=with_for_update
        )
        return instance

    @inject_session
    async def delete(self, instance: SQLModel, *, session: AsyncSession = None):
        session.add(instance)
        await session.delete(instance)
        await session.commit()

    @inject_session
    async def bulk_delete(
        self,
        instances: Iterable[SQLModel],
        *,
        session: AsyncSession | None = None,
    ):
        """Delete all given instances.

        Docs: https://docs.sqlalchemy.org/en/20/orm/session_basics.html#deleting"""
        async with session.begin():
            try:
                session.add_all(instances)
            except InvalidRequestError:
                pass

            await asyncio.gather(*[session.delete(instance) for instance in instances])
        await session.commit()

    @inject_session
    async def truncate(self, instance: SQLModel, *, session: AsyncSession = None):
        await session.execute(delete(instance))
        await session.commit()


async def get_db_service():
    async with DBService() as db:
        yield db


DBServiceDep = Annotated[DBService, Depends(get_db_service)]
