from http import HTTPStatus

from apps.authorization.models import Permission
from apps.hero.models import Hero
from apps.user.models import User
from core.testing.async_case import AsyncTestCase


class TestUserPermission(AsyncTestCase):
    fixtures = [
        "users",
        "heroes",
    ]

    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.user = await User.get(username="test")
        await Permission.generate_crud_objects(Hero.table_name())

    async def test_user_has_no_rights_to_edit_resource(self):
        hero_id = 1
        await self.client.user_login(self.user)

        data = {"secret_name": "test edit"}
        response = await self.client.patch(f"/heroes/{hero_id}/", json=data)
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)
        self.assertEqual(
            response.json()["detail"],
            "You do not have sufficient rights to this resource.",
        )

    async def test_user_has_rights_to_edit_resource(self):
        hero_id = 1
        await self.client.user_login(self.user)
        update_permission_name = Permission.format_permission_name(
            "update", Hero.table_name()
        )
        await self.add_permissions(self.user, [update_permission_name])

        data = {"secret_name": "test edit"}
        response = await self.client.patch(f"/heroes/{hero_id}/", json=data)
        self.assertEqual(HTTPStatus.OK, response.status_code)

        actual_data = response.json()
        hero = await Hero.get(id=hero_id)
        self.assertEqual(hero_id, hero.id)
        self.assertEqual(data["secret_name"], hero.secret_name)
        self.assertEqual(actual_data["secret_name"], data["secret_name"])
        self.assertEqual(actual_data["id"], hero_id)
