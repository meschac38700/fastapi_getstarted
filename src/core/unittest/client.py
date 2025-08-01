from httpx import AsyncClient
from httpx._types import HeaderTypes

from apps.authentication.models import JWTToken
from apps.user.models import User


class AsyncClientTest(AsyncClient):
    _token: JWTToken | None = None

    def __init__(self, *, headers: HeaderTypes | None = None, **kwargs):
        _headers = headers or {
            "Accept": "application/json",
        }
        super().__init__(headers=_headers, **kwargs)

    async def user_login(self, user: User):
        self._token = await JWTToken.get_or_create(user)
        self.headers.update(
            {"Authorization": f"{self._token.token_type} {self._token.access_token}"}
        )

    async def login(self, username: str) -> User:
        user = await User.get(username=username)
        await self.user_login(user)
        return user

    async def force_login(self, user: User):
        await self.logout()
        await self.user_login(user)

    async def logout(self) -> None:
        if self._token is None:
            return

        await self._token.delete()
        self.headers.pop("Authorization", None)
        self._token = None

    @property
    def user(self):
        """Return the current authenticated user."""
        if self._token is None:
            return None

        return self._token.user

    @property
    def token(self):
        """Return the current authenticated JWT token."""
        return self._token
