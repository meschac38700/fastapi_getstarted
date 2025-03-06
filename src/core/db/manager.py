from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from sqlalchemy.sql._typing import ColumnExpressionArgument
from sqlmodel import SQLModel

from .dependency import DBService

Fn = Callable[..., Any]
T = TypeVar("T", bound=SQLModel)


def session_decorator(func: Fn) -> Fn:
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

    @session_decorator
    async def insert(self, item: SQLModel):
        return await self.db_service.insert(item)

    @session_decorator
    async def insert_batch(
        self,
        data: list[SQLModel],
        *,
        batch_size: int = 50,
    ):
        """Insert a batch of SQLModel instances."""
        await self.db_service.insert_batch(data, batch_size=batch_size)

    @session_decorator
    async def get(self, **filters):
        return await self.db_service.get(self.model_class, **filters)

    @session_decorator
    async def all(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ):
        """Get all items of the given model."""
        return await self.db_service.all(self.model_class, offset=offset, limit=limit)

    @session_decorator
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

    @session_decorator
    async def exists(self, filters: ColumnExpressionArgument[bool] | bool) -> bool:
        return await self.db_service.exists(self.model_class, filters)

    @session_decorator
    async def delete(self, item: SQLModel):
        await self.db_service.delete(item)

    @session_decorator
    async def refresh(self, item: SQLModel) -> SQLModel:
        return await self.db_service.refresh(item)

    @session_decorator
    async def truncate(self):
        await self.db_service.truncate(self.model_class)
