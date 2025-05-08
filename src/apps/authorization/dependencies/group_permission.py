import logging
from http import HTTPStatus
from typing import Any, Callable

from fastapi import HTTPException

from apps.authentication.models import JWTToken
from apps.authorization.models import Group, Permission
from core.monitoring.logger import get_logger

Fn = Callable[..., Any]
_logger = get_logger(__name__)


def group_permission_required(
    groups: list[str],
    *,
    token: JWTToken,
    permissions: list[str] | None = None,
    any_match: bool = False,
    logger: logging.Logger | None = None,
) -> Fn:
    log = logger or _logger

    async def dependency():
        detail = "You do not have sufficient rights to this resource."
        user = token.user
        if user.is_admin:
            return user

        group_list = await Group.filter(name__in=groups)
        if not group_list:
            log.debug(f"Permission denied: groups not found: {group_list}.")
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=detail)

        user_belongs_groups, group_list = user.belongs_to_groups(
            group_list, any_match=any_match
        )
        if not user_belongs_groups:
            log.debug(
                f"Permission denied: user({user.username}) does not belong to groups: {groups}"
            )
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=detail)

        # scenario: We just need to check that the user belongs to certain groups
        if not permissions:
            return user

        permission_list = await Permission.filter(name__in=permissions)
        at_least_one_group_has_permission = any(
            grp.has_permissions(permission_list, any_match=any_match)
            for grp in group_list
        )
        if not at_least_one_group_has_permission:
            any_all = {"Any" if any_match else "All"}
            msg = f"{any_all} of Permission(s)({permission_list}) denied on groups: {group_list}"
            log.debug(msg)
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=detail)

        return user

    return dependency
