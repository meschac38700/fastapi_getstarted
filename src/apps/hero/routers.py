from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query

from apps.authorization.dependencies import permission_required
from apps.authorization.models import Permission

from .models import Hero
from .models.pydantic.create import HeroCreate
from .models.pydantic.patch import HeroPatch

routers = APIRouter(tags=["Heroes"], prefix="/heroes")
perms = {
    "create": Permission.format_permission_name("create", Hero.table_name()),
    "read": Permission.format_permission_name("read", Hero.table_name()),
    "update": Permission.format_permission_name("update", Hero.table_name()),
    "delete": Permission.format_permission_name("delete", Hero.table_name()),
}


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
        Depends(
            permission_required(permissions=[perms["create"]], groups=[perms["create"]])
        )
    ],
)
async def create_hero(hero: HeroCreate):
    return await Hero(**hero.model_dump()).save()


@routers.put(
    "/{pk}/",
    name="Update hero",
    response_model=Hero,
    status_code=HTTPStatus.OK,
    dependencies=[
        Depends(
            permission_required(permissions=[perms["update"]], groups=[perms["update"]])
        )
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
        Depends(
            permission_required(permissions=[perms["update"]], groups=[perms["update"]])
        )
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
        Depends(
            permission_required(permissions=[perms["delete"]], groups=[perms["delete"]])
        )
    ],
)
async def delete_hero(pk: int):
    stored_hero: Hero = await Hero.get(id=pk)
    if stored_hero is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Hero not found.")

    await stored_hero.delete()
