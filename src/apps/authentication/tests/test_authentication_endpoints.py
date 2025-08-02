from http import HTTPStatus

from apps.user.models import User
from core.unittest.async_case import AsyncTestCase


class TestAuthenticationEndpoints(AsyncTestCase):
    fixtures = ["users"]

    async def test_login_undefined_user(self, app):
        data = {
            "username": "sqdsq",
            "password": (lambda: "qsdz")(),
        }
        response = await self.client.post(app.url_path_for("jwt-auth"), data=data)
        assert response.status_code == HTTPStatus.NOT_FOUND

        assert response.json() == {"detail": "Authentication error: user not found."}

    async def test_login_bad_request(self, app):
        user = await User.get(id=1)
        data = {
            "username": user.username,
            "password": (lambda: "test")(),
        }
        response = await self.client.post(app.url_path_for("jwt-auth"), data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json() == {
            "detail": "Authentication error: credentials are invalid."
        }

    async def test_login_success(self, app):
        user = await User.get(username="fastapi")
        data = {
            "username": user.username,
            "password": (lambda: "fastapi")(),
        }
        response = await self.client.post(app.url_path_for("jwt-auth"), data=data)
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert list(data.keys()) == ["access_token", "token_type"]

    async def test_refresh_token(self, app):
        await self.client.login(username="fastapi")
        assert self.client.token is not None
        old_access_token = self.client.token.access_token
        assert self.client.token.can_be_refreshed

        response = await self.client.post(app.url_path_for("jwt-auth-refresh"))
        assert response.status_code == HTTPStatus.OK

        assert response.json()["access_token"] != old_access_token
