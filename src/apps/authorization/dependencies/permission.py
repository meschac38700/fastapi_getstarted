from fastapi import Depends, HTTPException

from apps.authentication.dependencies import oauth2_scheme

from .group_permission import group_permission_required
from .user_permission import user_permission_required


def permission_required(
    *,
    permissions: list[str] = None,
    groups: list[str] = None,
    any_match: bool = False,
):
    async def dependency(token=Depends(oauth2_scheme())):
        try:
            return await user_permission_required(
                permissions or [], any_match=any_match, token=token
            )()
        except HTTPException as e:
            if groups is None:
                raise HTTPException(status_code=e.status_code, detail=e.detail) from e

            return await group_permission_required(
                groups or [], permissions=permissions, any_match=any_match, token=token
            )()

    return dependency
