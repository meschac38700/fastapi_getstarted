from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from core.auth.dependencies import oauth2_scheme

from .models import User
from .models.pydantic.create import UserCreate
from .models.pydantic.patch import UserPatch

routers = APIRouter(tags=["users"], prefix="/users")


@routers.get("/", status_code=HTTPStatus.OK)
async def get_users(offset: int = 0, limit=100):
    return await User.all(offset=offset, limit=limit)


@routers.get("/{pk}", status_code=HTTPStatus.OK)
async def get_user(pk: int):
    return await User.get(User.id == pk)


@routers.put(
    "/{pk}", status_code=HTTPStatus.OK, dependencies=[Depends(oauth2_scheme())]
)
async def update_user(pk: int, user: UserCreate):
    stored_user = await User.get(User.id == pk)
    if stored_user is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found.")

    user.check_all_required_fields_updated(stored_user.model_dump())
    if not user.is_updated:
        return stored_user

    stored_user.update_from_dict(user.model_dump())
    return await stored_user.save()


@routers.patch(
    "/{pk}", status_code=HTTPStatus.OK, dependencies=[Depends(oauth2_scheme())]
)
async def patch_user(pk: int, user: UserPatch):
    stored_user = await User.get(User.id == pk)
    if stored_user is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found.")

    if user.check_all_fields_updated(stored_user.model_dump()):
        detail = "Cannot use PATCH to update entire object, use PUT instead."
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=detail)

    if not user.is_updated:
        return stored_user

    stored_user.update_from_dict(user.model_dump(exclude_unset=True))
    return await stored_user.save()


@routers.post(
    "/", status_code=HTTPStatus.CREATED, dependencies=[Depends(oauth2_scheme())]
)
async def post_user(user: UserCreate):
    return await User(**user.model_dump(exclude_unset=True)).save()


@routers.delete(
    "/{pk}", status_code=HTTPStatus.NO_CONTENT, dependencies=[Depends(oauth2_scheme())]
)
async def delete_user(pk: int):
    stored_user = await User.get(User.id == pk)
    if stored_user is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found.")

    return await stored_user.delete()
