from http import HTTPStatus
from typing import Any, Callable

from fastapi import HTTPException

from apps.authentication.models import JWTToken
from apps.authorization.models.permission import Permission

Fn = Callable[..., Any]


def user_permission_required(
    permissions: list[str],
    *,
    token: JWTToken,
    any_match: bool = False,
) -> Fn:
    async def dependency():
        permission_list = await Permission.filter(Permission.name.in_(permissions))
        user_has_permission = token.user.has_permissions(
            permission_list, any_match=any_match
        )
        if not user_has_permission:
            detail = "You do not have sufficient rights to this resource."
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=detail)

        return token.user

    return dependency
