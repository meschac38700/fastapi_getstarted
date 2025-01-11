from collections.abc import Iterable, Sequence
from typing import Self

from sqlalchemy.sql._typing import ColumnExpressionArgument
from sqlmodel import SQLModel

from core.db.manager import ModelManager


class ModelQuery:
    @classmethod
    def objects(cls) -> ModelManager:
        return ModelManager(cls)

    @classmethod
    async def get(cls, filter_by: ColumnExpressionArgument[bool] | bool) -> Self | None:
        return await cls.objects().get(filter_by)

    @classmethod
    async def filter(
        cls,
        filter_by: ColumnExpressionArgument[bool] | bool,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[Self]:
        return await cls.objects().filter(filter_by, offset=offset, limit=limit)

    @classmethod
    async def all(cls, *, offset: int = 0, limit: int = 100) -> Sequence[Self]:
        return await cls.objects().all(offset=offset, limit=limit)

    async def save(self) -> Self:
        return await self.objects().insert(self.model_dump())

    async def delete(self) -> None:
        return await self.objects().delete(self)

    @classmethod
    async def batch_create(
        cls, items: Iterable[SQLModel], *, batch_size: int = 50
    ) -> None:
        await cls.objects().insert_batch(items, batch_size=batch_size)
