from http import HTTPStatus

import settings
from apps.user.models import User
from core.unittest.async_case import AsyncTestCase


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

    async def test_refresh_token(self):
        await self.client.login(username="fastapi")
        self.assertIsNotNone(self.client.token)
        old_access_token = self.client.token.access_token
        self.assertTrue(self.client.token.can_be_refreshed)

        response = await self.client.post(f"{settings.AUTH_PREFIX_URL}/token/refresh")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertNotEqual(response.json()["access_token"], old_access_token)
