from http import HTTPStatus

from apps.authentication.models import JWTToken
from apps.authorization.models import Permission
from apps.user.models import User
from core.unittest.async_case import AsyncTestCase


class TestOAuth2Scheme(AsyncTestCase):
    fixtures = [
        "users",
    ]

    async def async_set_up(self):
        await super().async_set_up()
        self.user = await User.get(username="test")
        await Permission.generate_crud_objects(User.table_name())

    async def test_deleted_token_should_invalid_authentication(self):
        update_permission = Permission.format_permission_name(
            "update", User.table_name()
        )
        await self.add_permissions(self.user, [update_permission])

        await self.client.login(self.user.username)

        response = await self.client.patch(
            f"/users/{self.user.id}/", json={"last_name": "DOE"}
        )
        assert HTTPStatus.OK == response.status_code

        await (await JWTToken.get(user_id=self.user.id)).delete()

        response = await self.client.patch("/users/1/", json={"last_name": "DOE"})
        assert HTTPStatus.UNAUTHORIZED == response.status_code
        assert "Invalid authentication token." == response.json()["detail"]
