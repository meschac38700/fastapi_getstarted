from http import HTTPStatus
from typing import Any, Callable, Literal

from fastapi import HTTPException

from apps.authentication.models import JWTToken
from apps.authorization.models.group import Group
from apps.authorization.models.permission import Permission

Fn = Callable[..., Any]


def group_permission_required(
    groups: list[str],
    *,
    token: JWTToken,
    permissions: list[str] | None = None,
    operator: Literal["AND", "OR"] = "AND",
) -> Fn:
    async def dependency():
        user = token.user
        user_belongs_to_grp = user.belongs_to_all_groups
        if operator.upper() == "OR":
            user_belongs_to_grp = user.belongs_to_any_groups

        group_list = await Group.filter(Group.name.in_(groups))
        user_belongs_groups, group_list = user_belongs_to_grp(group_list)
        detail = "You do not have sufficient rights to this resource."
        if not user_belongs_groups:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=detail)

        # scenario: that we just check that the user belongs to certain groups
        if not permissions:
            return user

        permission_list = await Permission.filter(Permission.name.in_(permissions))
        at_least_one_group_has_permission = any(
            grp.has_permissions(permission_list, operator) for grp in group_list
        )
        if not at_least_one_group_has_permission:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=detail)

        return user

    return dependency
