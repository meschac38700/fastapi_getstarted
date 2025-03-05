from collections.abc import Iterable, Sequence
from typing import Self

from sqlmodel import SQLModel

from core.db.manager import ModelManager
from core.db.query.operators import QueryExpressionManager


class ModelQuery(QueryExpressionManager):
    @classmethod
    def objects(cls) -> ModelManager:
        return ModelManager(cls)

    @classmethod
    async def get(cls, **filters) -> Self | None:
        return await cls.objects().get(**filters)

    @classmethod
    async def filter(
        cls, *, offset: int = 0, limit: int = 100, **filters
    ) -> Sequence[Self]:
        return await cls.objects().filter(**filters, offset=offset, limit=limit)

    @classmethod
    async def all(cls, *, offset: int = 0, limit: int = 100) -> Sequence[Self]:
        return await cls.objects().all(offset=offset, limit=limit)

    async def save(self) -> Self:
        return await self.objects().insert(self)

    async def delete(self) -> None:
        return await self.objects().delete(self)

    @classmethod
    async def batch_create(
        cls, items: Iterable[SQLModel], *, batch_size: int = 50
    ) -> None:
        await cls.objects().insert_batch(items, batch_size=batch_size)

    async def refresh(self) -> Self:
        return await self.objects().refresh(self)
