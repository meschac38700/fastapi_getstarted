from http import HTTPStatus

from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer

import settings
from apps.authentication.models import JWTToken


def oauth2_scheme():
    async def wrapper(
        token=Depends(OAuth2PasswordBearer(tokenUrl=settings.AUTH_URL)),
    ) -> JWTToken:
        stored_token = await JWTToken.get(JWTToken.access_token == token)

        if stored_token is None:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Invalid authentication token.",
            )

        return stored_token

    return wrapper
