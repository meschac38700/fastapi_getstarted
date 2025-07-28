from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from apps.authentication.dependencies.oauth2 import current_user
from apps.user.dependencies.roles import AdminAccess
from apps.user.models import User

routers = APIRouter()


@routers.get("/groups/", name="List authenticated user's groups")
def get_authenticated_user_groups(auth_user: User = Depends(current_user)):
    return auth_user.groups


@routers.get(
    "/{pk}/groups/",
    name="Admin endpoint: List the specified user's groups",
    dependencies=[Depends(AdminAccess())],
)
async def get_user_groups(pk: int):
    stored_user = await User.get(id=pk)
    if stored_user is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found.")

    return stored_user.groups
