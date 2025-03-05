from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query

from apps.authorization.dependencies import permission_required

from .models import Hero
from .models.pydantic.create import HeroCreate
from .models.pydantic.patch import HeroPatch

routers = APIRouter(tags=["Heroes"], prefix="/heroes")


@routers.get("/{pk}/", name="Get hero by id.")
async def get_hero(pk: int):
    return await Hero.get(id=pk)


@routers.get("/", name="Get heroes")
async def get_heroes(
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    return await Hero.all(offset=offset, limit=limit)


@routers.post(
    "/",
    name="Create hero",
    response_model=Hero,
    status_code=HTTPStatus.CREATED,
    dependencies=[
        Depends(permission_required(["create_hero"], groups=["create_hero"]))
    ],
)
async def create_hero(hero: HeroCreate):
    _hero = await Hero(**hero.model_dump()).save()
    return _hero


@routers.put(
    "/{pk}/",
    name="Update hero",
    response_model=Hero,
    status_code=HTTPStatus.OK,
    dependencies=[
        Depends(permission_required(["update_hero"], groups=["update_hero"]))
    ],
)
async def update_hero(pk: int, hero: HeroCreate):
    stored_hero: Hero = await Hero.get(id=pk)
    if stored_hero is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Hero not found.")

    if not hero.check_all_required_fields_updated(stored_hero.model_dump()):
        detail = "Cannot use PUT to partially update registry, use PATCH instead."
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=detail)

    if not hero.is_updated:
        return stored_hero

    stored_hero.update_from_dict(hero.model_dump(exclude_unset=True))
    return await stored_hero.save()


@routers.patch(
    "/{pk}/",
    name="Patch hero",
    response_model=Hero,
    status_code=HTTPStatus.OK,
    dependencies=[
        Depends(permission_required(["update_hero"], groups=["update_hero"]))
    ],
)
async def patch_hero(pk: int, hero: HeroPatch):
    stored_hero: Hero = await Hero.get(id=pk)
    if stored_hero is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Hero not found.")

    if hero.check_all_fields_updated(stored_hero.model_dump()):
        detail = "Cannot use PATCH to update entire registry, use PUT instead."
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=detail)

    if not hero.is_updated:
        return stored_hero

    stored_hero.update_from_dict(hero.model_dump(exclude_unset=True))
    return await stored_hero.save()


@routers.delete(
    "/{pk}/",
    name="Delete hero",
    status_code=HTTPStatus.NO_CONTENT,
    dependencies=[
        Depends(permission_required(["delete_hero"], groups=["delete_hero"]))
    ],
)
async def delete_hero(pk: int):
    stored_hero: Hero = await Hero.get(id=pk)
    if stored_hero is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Hero not found.")

    await stored_hero.delete()
