from http import HTTPStatus

from apps.authentication.models import JWTToken
from apps.user.models import User
from core.test.async_case import AsyncTestCase


class TestOAuth2Scheme(AsyncTestCase):
    fixtures = [
        "users",
    ]

    async def test_deleted_token_should_invalid_authentication(self):
        user = await User.get(User.username == "fastapi")
        token = await JWTToken.get_or_create(user)

        await self.client.login(user.username)

        response = await self.client.patch("/users/1", json={"last_name": "DOE"})
        self.assertEqual(HTTPStatus.OK, response.status_code)

        await token.delete()

        response = await self.client.patch("/users/1", json={"last_name": "DOE"})
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)
        self.assertEqual("Invalid authentication token.", response.json()["detail"])
