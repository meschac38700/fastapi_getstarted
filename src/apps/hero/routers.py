from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Query

from services.db import DBService

from .models import Hero

routers = APIRouter(tags=["heroes"], prefix="/heroes")


@routers.get("/", name="Get heroes")
async def get_items(offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    async with DBService() as db_service:
        return await db_service.all(Hero, offset=offset, limit=limit)
