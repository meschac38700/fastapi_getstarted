from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Query

from services import DBServiceDep

from .models import Hero

routers = APIRouter(tags=["heroes"], prefix="/heroes")


@routers.get("/", name="Get heroes")
async def get_heroes(
    db_service: DBServiceDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    return await db_service.all(Hero, offset=offset, limit=limit)
