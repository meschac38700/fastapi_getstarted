from sqlalchemy.ext.asyncio import AsyncEngine

from apps.hero.faker import fake_heroes
from core.db import create_db_and_tables, delete_db_and_tables


async def setup(engine: AsyncEngine):
    """Script to be run after fastapi setup."""
    await create_db_and_tables(engine)
    await fake_heroes()


async def teardown(engine: AsyncEngine):
    """Script to be run before fastapi shutdown."""
    await delete_db_and_tables(engine)
