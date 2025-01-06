from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql._typing import ColumnExpressionArgument
from sqlmodel import SQLModel, select

from settings import settings


class DBService:
    """Group some utility functions for db queries."""

    def __init__(self):
        self._engine = settings.get_engine()

    async def insert_batch(self, instances: list[SQLModel]):
        """Insert a batch of SQLModel instances."""

        async with AsyncSession(self._engine) as session:
            session.add_all(instances)
            await session.commit()

    async def all(self, model: SQLModel, *, offset: int = 0, limit: int = 100):
        """Get all items of the given model."""

        async with AsyncSession(self._engine) as session:
            # based on https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#dynamic-asyncio
            data = await session.scalars(select(model).offset(offset).limit(limit))

        return data.all()

    async def filter(
        self,
        model: SQLModel,
        filters: ColumnExpressionArgument[bool] | bool,
        *,
        offset: int = 0,
        limit: int = 100,
    ):
        async with AsyncSession(self._engine) as session:
            data_list = await session.scalars(
                select(model).where(filters).offset(offset).limit(limit)
            )
        return data_list.all()

    # TODO(Complete with others functions)


@lru_cache
def get_db_service():
    return DBService()
