from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import and_

from apps.authorization.models.permission import Permission
from apps.authorization.models.pydantic import (
    PermissionCreate,
    PermissionUpdate,
)
from apps.user.dependencies.roles import AdminAccess

routers = APIRouter(tags=["authorization"], prefix="/authorizations")


@routers.get(
    "/permissions",
    name="List all app permissions",
    dependencies=[Depends(AdminAccess())],
)
async def get_permissions(
    name: str | None = None,
    target_table: str | None = None,
    offset: int = 0,
    limit: int = 100,
):
    filters = []
    if name is not None:
        filters.append(Permission.name == name)

    if target_table is not None:
        filters.append(Permission.target_table == target_table)

    return await (
        Permission.filter(and_(*filters), offset=offset, limit=limit)
        if filters
        else Permission.all(offset=offset, limit=limit)
    )


@routers.post(
    "/permissions",
    name="Create new Permission",
    dependencies=[Depends(AdminAccess())],
    status_code=HTTPStatus.CREATED,
)
async def create_permission(permission_data: PermissionCreate):
    return await Permission(**permission_data.model_dump()).save()


@routers.patch(
    "/permissions/{pk}",
    name="Patch a Permission",
    dependencies=[Depends(AdminAccess())],
)
async def patch_permission(pk: int, permission_data: PermissionUpdate):
    permission = await Permission.get(Permission.id == pk)
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
    "/permissions/{pk}",
    name="Update a Permission",
    dependencies=[Depends(AdminAccess())],
)
async def put_permission(pk: int, permission_data: PermissionCreate):
    permission = await Permission.get(Permission.id == pk)
    if permission is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Permission not found."
        )
    # if all required fields are not updated, pydantic error will be generated (PermissionCreate)
    permission_data.check_all_required_fields_updated(permission.model_dump())
    if not permission_data.is_updated:
        return permission

    permission.update_from_dict(permission_data.model_dump(exclude_unset=True))

    return await permission.save()
