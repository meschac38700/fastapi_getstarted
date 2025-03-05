from http import HTTPStatus

from apps.authentication.models import JWTToken
from apps.authorization.models.permission import Permission
from apps.user.models import User
from core.test.async_case import AsyncTestCase


class TestOAuth2Scheme(AsyncTestCase):
    fixtures = [
        "users",
    ]

    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.user = await User.get(username="test")
        # TODO(Eliam): remove once test in docker task done
        await Permission.generate_crud_objects(User.table_name())

    async def test_deleted_token_should_invalid_authentication(self):
        await self.add_permissions(self.user, ["update_user"])

        await self.client.login(self.user.username)

        response = await self.client.patch(
            f"/users/{self.user.id}/", json={"last_name": "DOE"}
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)

        await (await JWTToken.get(user_id=self.user.id)).delete()

        response = await self.client.patch("/users/1/", json={"last_name": "DOE"})
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)
        self.assertEqual("Invalid authentication token.", response.json()["detail"])
