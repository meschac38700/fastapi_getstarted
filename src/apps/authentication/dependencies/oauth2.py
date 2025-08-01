from http import HTTPStatus

from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer

from apps.authentication.models import JWTToken
from apps.user.models import User
from settings import settings


def oauth2_scheme():
    async def wrapper(
        token=Depends(OAuth2PasswordBearer(tokenUrl=settings.AUTH_URL)),
    ) -> JWTToken:
        stored_token = await JWTToken.get(access_token=token)

        if stored_token is None:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Invalid authentication token.",
            )

        if stored_token.is_expired:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Your session has expired.",
            )

        if stored_token.user is None:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Invalid authentication token. user does not exist.",
            )

        return stored_token

    return wrapper


def current_user():
    def dependency(token: JWTToken = Depends(oauth2_scheme())) -> User:
        return token.user

    return dependency
