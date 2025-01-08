from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Query

from services import DBServiceDep

from .models import Hero
from .models.validation_types import HeroCreate

routers = APIRouter(tags=["heroes"], prefix="/heroes")


@routers.get("/{pk}", name="Get hero by id.")
async def get_hero(pk: int, db_service: DBServiceDep):
    return await db_service.get(Hero, Hero.id == pk)


@routers.get("/", name="Get heroes")
async def get_heroes(
    db_service: DBServiceDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    return await db_service.all(Hero, offset=offset, limit=limit)


@routers.post(
    "/", name="Create hero", response_model=Hero, status_code=HTTPStatus.CREATED
)
async def create_hero(hero: HeroCreate, db_service: DBServiceDep):
    _hero = Hero(**hero.model_dump())
    await db_service.insert(_hero)
    return _hero
