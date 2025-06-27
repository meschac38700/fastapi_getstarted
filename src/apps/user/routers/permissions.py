from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends

from apps.authentication.dependencies.oauth2 import current_user
from apps.authorization.models.schema.permission import PermissionList
from apps.user.dependencies.roles import AdminAccess
from apps.user.models import User

_NOT_FOUND_MSG = "User not found."

routers = APIRouter()


@routers.get("/permissions/", name="List current authenticated user's permissions")
async def get_authenticated_user_permissions(auth_user: User = Depends(current_user())):
    return auth_user.get_permissions()


@routers.get(
    "/{pk}/permissions/",
    name="Admin endpoint: List the specified user's permissions",
    dependencies=[Depends(AdminAccess())],
)
async def get_user_permissions(pk: int):
    stored_user = await User.get(id=pk)
    if stored_user is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=_NOT_FOUND_MSG)

    return stored_user.get_permissions()


@routers.patch(
    "/{pk}/permissions/add/",
    name="Admin endpoint: Add some permissions to a certain user",
    dependencies=[Depends(AdminAccess())],
)
async def add_permissions_user(pk: int, permissions: PermissionList):
    stored_user = await User.get(id=pk)
    if stored_user is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=_NOT_FOUND_MSG)

    added_perms = await permissions.to_object_list()
    await stored_user.extend_permissions(added_perms)

    return added_perms


@routers.patch(
    "/{pk}/permissions/remove/",
    name="Admin endpoint: Remove some permissions to a certain user",
    dependencies=[Depends(AdminAccess())],
)
async def remove_permissions_user(pk: int, permissions: PermissionList):
    stored_user = await User.get(id=pk)
    if stored_user is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=_NOT_FOUND_MSG)

    removed_perms = await permissions.to_object_list()
    await stored_user.remove_permissions(removed_perms)

    return removed_perms
