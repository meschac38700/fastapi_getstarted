from httpx import AsyncClient

from apps.authentication.models import JWTToken
from apps.user.models import User


class AsyncClientTest(AsyncClient):
    _token: JWTToken | None = None

    async def login(self, username: str) -> User:
        user = await User.get(User.username == username)
        self._token = await JWTToken.get_or_create(user)
        self.headers.update({"Authorization": f"Bearer {self._token.access_token}"})
        return user

    async def logout(self) -> None:
        if self._token is None:
            return

        await self._token.delete()
        self._token = None
