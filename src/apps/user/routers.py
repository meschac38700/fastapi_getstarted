from http import HTTPStatus

from fastapi import APIRouter

from .models import User

routers = APIRouter(tags=["users"], prefix="/users")


@routers.get("/", status_code=HTTPStatus.OK)
async def get_users(offset: int = 0, limit=100):
    return await User.all(offset=offset, limit=limit)


@routers.get("/{pk}", status_code=HTTPStatus.OK)
async def get_user(pk: int):
    return await User.get(User.id == pk)
