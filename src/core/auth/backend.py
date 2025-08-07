from fastapi.security import OAuth2PasswordBearer
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    BaseUser,
)
from starlette.requests import HTTPConnection

from apps.authentication.dependencies.oauth2 import current_session_user
from apps.authentication.models import JWTToken
from settings import settings


class AuthBackend(AuthenticationBackend):
    async def authenticate(
        self, conn: HTTPConnection
    ) -> tuple[AuthCredentials, BaseUser] | None:
        user = await current_session_user(conn)
        if user is None:
            oauth2 = OAuth2PasswordBearer(tokenUrl=settings.AUTH_URL, auto_error=False)
            if (token := await oauth2(conn)) is not None:
                jwt_token = await JWTToken.get(access_token=token)
                if jwt_token is not None:
                    user = jwt_token.user

        if user is None:
            return None

        return AuthCredentials(["authenticated"]), user
