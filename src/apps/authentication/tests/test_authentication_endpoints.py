from http import HTTPStatus

import settings
from apps.user.models import User
from core.testing.async_case import AsyncTestCase


class TestAuthenticationEndpoints(AsyncTestCase):
    fixtures = ["users"]

    async def test_login_undefined_user(self):
        data = {
            "username": "sqdsq",
            "password": "qsdz",
        }
        response = await self.client.post(
            f"{settings.AUTH_PREFIX_URL}/token", data=data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        self.assertEqual(
            response.json(), {"detail": "Authentication error: user not found."}
        )

    async def test_login_bad_request(self):
        user = await User.get(id=1)
        data = {
            "username": user.username,
            "password": "test",
        }
        response = await self.client.post(
            f"{settings.AUTH_PREFIX_URL}/token", data=data
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {"detail": "Authentication error: credentials are invalid."},
        )

    async def test_login_success(self):
        user = await User.get(username="fastapi")
        data = {
            "username": user.username,
            "password": "fastapi",
        }
        response = await self.client.post(
            f"{settings.AUTH_PREFIX_URL}/token", data=data
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        self.assertListEqual(list(data.keys()), ["access_token", "token_type"])
