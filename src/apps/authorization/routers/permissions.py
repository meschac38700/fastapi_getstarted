from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from apps.authorization.models.permission import Permission
from apps.authorization.models.pydantic.permission import (
    PermissionCreate,
    PermissionUpdate,
)
from apps.user.dependencies.roles import AdminAccess

routers = APIRouter()


@routers.get(
    "/",
    name="List all app permissions",
    dependencies=[Depends(AdminAccess())],
)
async def get_permissions(
    name: str | None = None,
    target_table: str | None = None,
    offset: int = 0,
    limit: int = 100,
):
    filters = {}
    if name is not None:
        filters["name"] = name

    if target_table is not None:
        filters["target_table"] = target_table

    return await (
        Permission.filter(**filters, offset=offset, limit=limit)
        if filters
        else Permission.all(offset=offset, limit=limit)
    )


@routers.post(
    "/",
    name="Create new Permission",
    dependencies=[Depends(AdminAccess())],
    status_code=HTTPStatus.CREATED,
)
async def create_permission(permission_data: PermissionCreate):
    return await Permission(**permission_data.model_dump()).save()


@routers.patch(
    "/{pk}/",
    name="Patch a Permission",
    dependencies=[Depends(AdminAccess())],
)
async def patch_permission(pk: int, permission_data: PermissionUpdate):
    permission = await Permission.get(id=pk)
    if permission is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Permission not found."
        )

    if permission_data.check_all_fields_updated(permission.model_dump()):
        detail = "Cannot use PATCH to update entire registry, use PUT instead."
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=detail)

    if not permission_data.is_updated:
        return permission

    permission.update_from_dict(permission_data.model_dump(exclude_unset=True))

    return await permission.save()


@routers.put(
    "/{pk}/",
    name="Update a Permission",
    dependencies=[Depends(AdminAccess())],
)
async def put_permission(pk: int, permission_data: PermissionCreate):
    permission = await Permission.get(id=pk)
    if permission is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Permission not found."
        )

    permission_data.check_all_required_fields_updated(permission.model_dump())
    if not permission_data.is_updated:
        return permission

    permission.update_from_dict(permission_data.model_dump(exclude_unset=True))

    return await permission.save()


@routers.delete(
    "/{pk}/",
    name="Delete a Permission",
    dependencies=[Depends(AdminAccess())],
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_permission(pk: int):
    permission = await Permission.get(id=pk)
    if permission is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Permission not found."
        )

    await permission.delete()
