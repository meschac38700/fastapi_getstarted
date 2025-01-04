from typing import Annotated

from fastapi import Depends
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession

from configs import db_settings


async def get_session():
    engine = db_settings.get_engine()
    async with AsyncSession(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
