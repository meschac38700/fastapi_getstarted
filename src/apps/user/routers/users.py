from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from apps.authentication.dependencies.oauth2 import current_user
from apps.authorization.dependencies import permission_required
from apps.user.models import User
from apps.user.models.pydantic.create import UserCreate
from apps.user.models.pydantic.patch import UserPatch

routers = APIRouter()


@routers.get("/", name="Get all users", status_code=HTTPStatus.OK)
async def get_users(offset: int = 0, limit=100):
    return await User.all(offset=offset, limit=limit)


@routers.get("/{pk}/", name="Get single user", status_code=HTTPStatus.OK)
async def get_user(pk: int):
    return await User.get(id=pk)


@routers.put(
    "/{pk}/",
    name="Update user",
    status_code=HTTPStatus.OK,
    dependencies=[
        Depends(permission_required(["update_user"], groups=["update_user"]))
    ],
)
async def update_user(
    pk: int, user: UserCreate, auth_user: User = Depends(current_user())
):
    stored_user = await User.get(id=pk)
    if stored_user is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found.")

    if not auth_user.is_admin and auth_user != stored_user:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="this action is prohibited with this user currently logged in",
        )

    user.check_all_required_fields_updated(stored_user.model_dump())
    if not user.is_updated:
        return stored_user

    stored_user.update_from_dict(user.model_dump())
    return await stored_user.save()


@routers.patch(
    "/{pk}/",
    status_code=HTTPStatus.OK,
    name="Patch user",
    dependencies=[
        Depends(permission_required(["update_user"], groups=["update_user"]))
    ],
)
async def patch_user(
    pk: int, user: UserPatch, auth_user: User = Depends(current_user())
):
    stored_user = await User.get(id=pk)
    if stored_user is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found.")

    if not auth_user.is_admin and auth_user != stored_user:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="this action is prohibited with this user currently logged in.",
        )

    if user.check_all_fields_updated(stored_user.model_dump()):
        detail = "Cannot use PATCH to update entire object, use PUT instead."
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=detail)

    if not user.is_updated:
        return stored_user

    stored_user.update_from_dict(user.model_dump(exclude_unset=True))
    return await stored_user.save()


@routers.post(
    "/",
    status_code=HTTPStatus.CREATED,
)
async def post_user(user: UserCreate):
    return await User(**user.model_dump(exclude_unset=True)).save()


@routers.delete(
    "/{pk}/",
    status_code=HTTPStatus.NO_CONTENT,
    dependencies=[
        Depends(
            permission_required(["delete_user"], groups=["delete_user"]),
        )
    ],
)
async def delete_user(pk: int, user: User = Depends(current_user())):
    stored_user = await User.get(id=pk)

    if stored_user is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found.")

    if not user.is_admin and user != stored_user:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="this action is prohibited with this user currently logged in",
        )

    return await stored_user.delete()
