from collections.abc import Iterable
from functools import lru_cache
from typing import Any, Self

from sqlmodel import SQLModel

from core.db.query.manager import ModelManager
from core.db.query.operators import QueryExpressionManager


class ModelQuery(QueryExpressionManager):
    @classmethod
    @lru_cache
    def objects(cls) -> ModelManager:
        return ModelManager(cls)

    @classmethod
    async def get(cls, **filters) -> Self | None:
        return await cls.objects().get(**filters)

    @classmethod
    async def first(cls) -> Self:
        return await cls.objects().first()

    @classmethod
    async def values(cls, *fields, filters: dict[str, Any] | None = None):
        """Select specific columns from database table.

        :example
          > import asyncio
          > from apps.user.models import User
          > asyncio.run( User.values("first_name", "last_name", "age", filters={"role": "admin"}) )
        """
        return await cls.objects().values(*fields, filters=filters)

    @classmethod
    async def filter(
        cls, *, offset: int = 0, limit: int = 100, **filters
    ) -> list[Self]:
        return await cls.objects().filter(**filters, offset=offset, limit=limit)

    @classmethod
    async def count(cls, **filters) -> int:
        return await cls.objects().count(**filters)

    @classmethod
    async def all(cls, *, offset: int = 0, limit: int = 100) -> list[Self]:
        return await cls.objects().all(offset=offset, limit=limit)

    async def save(self) -> Self:
        return await self.objects().insert(self)

    async def delete(self) -> None:
        return await self.objects().delete(self)

    @classmethod
    async def bulk_delete(cls, items: Iterable[SQLModel]):
        return await cls.objects().bulk_delete(items)

    async def refresh(self) -> Self:
        return await self.objects().refresh(self)

    async def exists(self) -> bool:
        return await self.objects().exists(self)

    @classmethod
    async def bulk_create_or_update(cls, items: Iterable[SQLModel]) -> None:
        await cls.objects().bulk_create_or_update(items)

    @classmethod
    async def truncate(cls) -> Self:
        return await cls.objects().truncate()
