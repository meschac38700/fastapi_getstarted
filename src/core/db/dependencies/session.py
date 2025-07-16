from typing import Annotated

from fastapi import Depends
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession


def get_engine(**kwargs) -> create_async_engine:
    """Create async database engine.

    Docs: https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html
    """
    from settings import settings

    kw = {"pool_pre_ping": True, "poolclass": NullPool, **kwargs}
    return create_async_engine(settings.uri, **kw)


async def get_session():
    engine = get_engine()
    async with AsyncSession(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
