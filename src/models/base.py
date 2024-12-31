from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class BaseAsyncModel(AsyncAttrs, DeclarativeBase):
    pass
