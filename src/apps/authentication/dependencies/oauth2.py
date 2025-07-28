from http import HTTPStatus

from fastapi import HTTPException, Request
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer

from apps.authentication.models import JWTToken
from apps.user.models import User
from settings import settings


async def current_session_user(request: Request):
    session_data = request.session.get(settings.session_user_key, None)
    if session_data is None:
        return None

    user = await User.get(username=session_data["username"])
    return user


def oauth2_scheme(auto_error: bool = True):
    async def wrapper(
        token=Depends(
            OAuth2PasswordBearer(tokenUrl=settings.AUTH_URL, auto_error=auto_error)
        ),
        session_user=Depends(current_session_user),
    ) -> JWTToken:
        """Manage both session and token authentication."""
        if session_user is not None:
            return await JWTToken.get(user=session_user)

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


def current_user(
    token: JWTToken = Depends(oauth2_scheme(auto_error=False)),
) -> User:
    if token is None:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Not authenticated"
        )
    return token.user
