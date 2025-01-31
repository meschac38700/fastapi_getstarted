from typing import Literal

from fastapi import Depends, HTTPException

from apps.authentication.dependencies import oauth2_scheme

from .group_permission import group_permission_required
from .user_permission import user_permission_required


def permission_required(
    permissions: list[str],
    *,
    groups: list[str] = None,
    operator: Literal["AND", "OR"] = "AND",
):
    async def dependency(token=Depends(oauth2_scheme())):
        try:
            return await user_permission_required(
                permissions, operator=operator, token=token
            )()
        except HTTPException as e:
            if groups is None:
                raise HTTPException(status_code=e.status_code, detail=e.detail) from e

            return await group_permission_required(
                groups, permissions=permissions, operator=operator, token=token
            )()

    return dependency
