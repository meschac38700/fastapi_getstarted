from httpx import AsyncClient

from apps.authentication.models import JWTToken
from apps.user.models import User


class AsyncClientTest(AsyncClient):
    _token: JWTToken | None = None

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
