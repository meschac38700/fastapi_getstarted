from http import HTTPStatus
from typing import Any, Callable, Literal

from fastapi import HTTPException

from apps.authentication.models import JWTToken
from apps.authorization.models.permission import Permission

Fn = Callable[..., Any]


def user_permission_required(
    permissions: list[str],
    *,
    token: JWTToken,
    operator: Literal["AND", "OR"] = "AND",
) -> Fn:
    async def dependency():
        check_perm = token.user.has_permissions
        if operator.upper() == "OR":
            check_perm = token.user.has_permission

        permission_list = await Permission.filter(Permission.name.in_(permissions))
        user_has_permission = check_perm(permission_list)
        if not user_has_permission:
            detail = "You do not have sufficient rights to this resource."
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=detail)

        return token.user

    return dependency
