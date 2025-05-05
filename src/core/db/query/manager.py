from collections.abc import Callable
from functools import wraps
from typing import Any, Iterable, ParamSpec, TypeVar

from sqlmodel import SQLModel

from core.db.dependencies import DBService

P = ParamSpec("P")
Fn = Callable[P, Any]
T = TypeVar("T", bound=SQLModel)


def connection_manager(func: Fn) -> Fn:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        self_obj: ModelManager = args[0]
        res = await func(*args, **kwargs)
        await self_obj.db_service.dispose()
        return res

    return wrapper


class ModelManager:
    """Group some utility functions for db queries."""

    def __init__(self, model_class: type[SQLModel]):
        super().__init__()
        self.model_class = model_class
        self.db_service = DBService()

    @property
    def session(self):
        return self.db_service.session

    @property
    def sync_session(self):
        return self.session.sync_session

    @connection_manager
    async def insert(self, item: SQLModel):
        return await self.db_service.insert(item)

    @connection_manager
    async def insert_batch(self, data: list[SQLModel]):
        """Insert a batch of SQLModel instances."""
        await self.db_service.insert_batch(data)

    @connection_manager
    async def get(self, **filters):
        return await self.db_service.get(self.model_class, **filters)

    @connection_manager
    async def values(self, *attrs, filters: dict[str, Any] | None = None):
        return await self.db_service.values(self.model_class, *attrs, filters=filters)

    @connection_manager
    async def all(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ):
        """Get all items of the given model."""
        return await self.db_service.all(self.model_class, offset=offset, limit=limit)

    @connection_manager
    async def filter(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        **filters,
    ):
        return await self.db_service.filter(
            self.model_class, **filters, offset=offset, limit=limit
        )

    @connection_manager
    async def exists(self, item: SQLModel) -> bool:
        return await self.db_service.exists(self.model_class, item)

    @connection_manager
    async def delete(self, item: SQLModel):
        await self.db_service.delete(item)

    @connection_manager
    async def bulk_delete(self, items: Iterable[SQLModel]):
        await self.db_service.bulk_delete(items)

    @connection_manager
    async def refresh(self, item: SQLModel) -> SQLModel:
        return await self.db_service.refresh(item)

    @connection_manager
    async def truncate(self):
        await self.db_service.truncate(self.model_class)
