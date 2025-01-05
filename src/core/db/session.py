from typing import Annotated

from fastapi import Depends
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession

from settings import settings


async def get_session():
    engine = settings.get_engine()
    async with AsyncSession(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
