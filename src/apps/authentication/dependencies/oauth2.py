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


def oauth2_scheme():
    async def wrapper(
        token: str | None = Depends(OAuth2PasswordBearer(tokenUrl=settings.AUTH_URL)),
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


async def current_user(
    request: Request,
    session_user: User = Depends(current_session_user),
) -> User:
    """Retrieve the current user either in the session or in the jwt token."""
    if session_user is not None:
        return session_user

    # Manually check retrieve user in jwt token to avoid an undesirable behavior
    # where the check on the token takes over with "Depends" approach
    token_check_callback = oauth2_scheme()
    oauth2 = OAuth2PasswordBearer(tokenUrl=settings.AUTH_URL)
    token_str = await oauth2(request=request)
    token: JWTToken = await token_check_callback(token_str)

    return token.user
