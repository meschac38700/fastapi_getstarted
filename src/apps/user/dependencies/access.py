from abc import abstractmethod

from fastapi import Depends

from apps.authentication.dependencies import oauth2_scheme
from apps.authentication.dependencies.oauth2 import current_session_user
from apps.authentication.models import JWTToken
from apps.user.dependencies.exceptions import AccessDeniedError
from apps.user.models import User
from core.routers.dependencies import AccessDependency


class UserAccess[T = User](AccessDependency[User]):
    user: User

    @abstractmethod
    def test_access(self) -> bool:
        pass

    async def __call__(self, token: JWTToken = Depends(oauth2_scheme())) -> T:
        self.user = token.user
        test_pass = self.test_access()

        if not test_pass:
            self.raise_access_denied()

        return self.user


class AnonymousUserAccess(UserAccess[User]):
    def test_access(self) -> bool:
        return True

    async def __call__(self, user: User = Depends(current_session_user)):
        if user is not None:
            raise AccessDeniedError()

        return None
