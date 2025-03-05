import logging
from http import HTTPStatus
from typing import Any, Callable

from fastapi import HTTPException

from apps.authentication.models import JWTToken
from apps.authorization.models.permission import Permission

Fn = Callable[..., Any]

_logger = logging.getLogger(__name__)


def user_permission_required(
    permissions: list[str],
    *,
    token: JWTToken,
    any_match: bool = False,
    logger: logging.Logger | None = None,
) -> Fn:
    log = logger or _logger

    async def dependency():
        detail = "You do not have sufficient rights to this resource."
        permission_list = await Permission.filter(name__in=permissions)

        if not permission_list:
            log.debug(f"Permission denied: permissions not found: {permissions}.")
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=detail)

        user_has_permission = token.user.has_permissions(
            permission_list, any_match=any_match
        )

        if not user_has_permission:
            any_all = f"{'any' if any_match else 'all'}"
            msg = f"Permission denied: user{token.user.username} does not have {any_all} of the following rights: {permissions}."
            log.debug(msg)
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail=detail)

        return token.user

    return dependency
