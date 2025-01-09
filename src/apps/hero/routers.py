from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Query

from services import DBServiceDep

from .models import Hero
from .models.validation_types import HeroCreate, HeroPatch, HeroUpdate

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


@routers.put(
    "/{pk}", name="Update hero", response_model=Hero, status_code=HTTPStatus.OK
)
async def update_hero(pk: int, hero: HeroUpdate, db_service: DBServiceDep):
    stored_hero: Hero = await db_service.get(Hero, Hero.id == pk)
    if stored_hero is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Hero not found.")

    stored_hero.update_from_dict(hero.model_dump(exclude_unset=True))
    await db_service.insert(stored_hero)
    return stored_hero


@routers.patch(
    "/{pk}", name="Update hero", response_model=Hero, status_code=HTTPStatus.OK
)
async def patch_hero(pk: int, hero: HeroPatch, db_service: DBServiceDep):
    stored_hero: Hero = await db_service.get(Hero, Hero.id == pk)
    if stored_hero is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Hero not found.")

    if hero.check_all_field_updated(stored_hero.model_dump()):
        detail = "Cannot use PATCH to update entire registry, use PUT instead."
        raise HTTPException(status_code=HTTPStatus.METHOD_NOT_ALLOWED, detail=detail)

    stored_hero.update_from_dict(hero.model_dump(exclude_unset=True))
    await db_service.insert(stored_hero)
    return stored_hero


@routers.delete("/{pk}", name="Delete hero", status_code=HTTPStatus.NO_CONTENT)
async def delete_hero(pk: int, db_service: DBServiceDep):
    stored_hero: Hero = await db_service.get(Hero, Hero.id == pk)
    if stored_hero is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Hero not found.")

    await db_service.delete(stored_hero)
