from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from settings import db_settings


class DBService:
    """Group some utility functions for queries."""

    def __init__(self):
        self._engine = db_settings.get_engine()

    async def insert_batch(self, items: list[SQLModel]):
        async with AsyncSession(self._engine) as session:
            session.add_all(items)
            await session.commit()

    # TODO(Complete with others functions)


@lru_cache
def get_db_service():
    return DBService()
