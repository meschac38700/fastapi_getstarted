from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import and_

from apps.authentication.dependencies.oauth2 import current_user
from apps.authorization.models.permission import Permission
from apps.user.models import User

routers = APIRouter(tags=["authorization"], prefix="/authorizations")


@routers.get("/permissions", name="List all app permissions")
async def get_permissions(
    name: str | None = None,
    target_table: str | None = None,
    offset: int = 0,
    limit: int = 100,
    user: User = Depends(current_user()),
):
    if not user.is_admin:
        detail = "You do not have sufficient rights to this resource."
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=detail)

    filters = []
    if name is not None:
        filters.append(Permission.name == name)

    if target_table is not None:
        filters.append(Permission.target_table == target_table)

    permission_query = Permission.all(offset=offset, limit=limit)
    if filters:
        permission_query = Permission.filter(and_(*filters), offset=offset, limit=limit)

    return await permission_query
