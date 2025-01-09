from sqlalchemy.ext.asyncio import AsyncEngine


async def setup(engine: AsyncEngine):
    """Script to be run after fastapi setup."""
    # await create_db_and_tables(engine)


async def teardown(engine: AsyncEngine):
    """Script to be run before fastapi shutdown."""
    # await delete_db_and_tables(engine)
