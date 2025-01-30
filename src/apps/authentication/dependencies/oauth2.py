from http import HTTPStatus

from fastapi import HTTPException, Request
from fastapi.security import OAuth2PasswordBearer

import settings
from apps.authentication.models import JWTToken
from core.auth import utils as auth_utils


def oauth2_scheme():
    async def wrapper(request: Request):
        _, token = auth_utils.jwt_token_from_request(request)
        stored_token = await JWTToken.get(JWTToken.access_token == token)

        if stored_token is None:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Invalid authentication token.",
            )

        return await OAuth2PasswordBearer(tokenUrl=settings.AUTH_URL)(request)

    return wrapper
