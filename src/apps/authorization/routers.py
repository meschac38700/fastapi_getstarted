from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlmodel import and_

from apps.authorization.models.permission import Permission
from apps.authorization.models.pydantic import PermissionCreate
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
