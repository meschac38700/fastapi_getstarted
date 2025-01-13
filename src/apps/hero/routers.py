from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Query

from .models import Hero
from .models.pydantic.create import HeroCreate
from .models.pydantic.patch import HeroPatch

routers = APIRouter(tags=["heroes"], prefix="/heroes")


@routers.get("/{pk}", name="Get hero by id.")
async def get_hero(pk: int):
    return await Hero.get(Hero.id == pk)


@routers.get("/", name="Get heroes")
async def get_heroes(
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    return await Hero.all(offset=offset, limit=limit)


@routers.post(
    "/", name="Create hero", response_model=Hero, status_code=HTTPStatus.CREATED
)
async def create_hero(hero: HeroCreate):
    _hero = await Hero(**hero.model_dump()).save()
    return _hero


@routers.put(
    "/{pk}", name="Update hero", response_model=Hero, status_code=HTTPStatus.OK
)
async def update_hero(pk: int, hero: HeroCreate):
    stored_hero: Hero = await Hero.get(Hero.id == pk)
    if stored_hero is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Hero not found.")

    if not hero.check_all_required_fields_updated(stored_hero.model_dump()):
        detail = "Cannot use PUT to partially update registry, use PATCH instead."
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=detail)

    stored_hero.update_from_dict(hero.model_dump(exclude_unset=True))
    return await stored_hero.save()


@routers.patch(
    "/{pk}", name="Update hero", response_model=Hero, status_code=HTTPStatus.OK
)
async def patch_hero(pk: int, hero: HeroPatch):
    stored_hero: Hero = await Hero.get(Hero.id == pk)
    if stored_hero is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Hero not found.")
    print("----------------------------------------------------+++++++")
    print(hero.check_all_field_updated(stored_hero.model_dump()))
    print("----------------------------------------------------+++++++")
    if hero.check_all_field_updated(stored_hero.model_dump()):
        detail = "Cannot use PATCH to update entire registry, use PUT instead."
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=detail)

    stored_hero.update_from_dict(hero.model_dump(exclude_unset=True))
    return await stored_hero.save()


@routers.delete("/{pk}", name="Delete hero", status_code=HTTPStatus.NO_CONTENT)
async def delete_hero(pk: int):
    stored_hero: Hero = await Hero.get(Hero.id == pk)
    if stored_hero is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Hero not found.")

    await stored_hero.delete()
