from http import HTTPStatus

from apps.authorization.models.group import Group
from apps.authorization.models.permission import Permission
from apps.hero.models import Hero
from apps.user.models import User
from core.test.async_case import AsyncTestCase


class TestGroupPermissions(AsyncTestCase):
    fixtures = [
        "users",
        "heroes",
    ]

    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.user = await User.get(User.username == "fastapi")
        # TODO(Eliam): Remove the following line of code once the test in docker container task completed
        await Permission.generate_crud_permissions(Hero.table_name())

    async def test_group_has_no_right_permissions_cannot_edit(self):
        self.read_group = await Group(
            name="read_hero", display_name="Read hero resources."
        ).save()
        await self.read_group.add_permission(
            await Permission.get(Permission.name == "read_hero")
        )
        await self.read_group.add_user(self.user)

        await self.client.user_login(self.user)

        data = {"secret_name": "Test edit"}
        response = await self.client.patch("/heroes/1", json=data)
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)
        self.assertEqual(
            response.json()["detail"],
            "You do not have sufficient rights to this resource.",
        )

    async def test_group_permission_to_edit_resource(self):
        self.edit_group = await Group(
            name="update_hero", display_name="Update hero resources."
        ).save()
        await self.edit_group.add_permission(
            await Permission.get(Permission.name == "update_hero")
        )
        await self.edit_group.add_user(self.user)

        await self.client.user_login(self.user)

        hero_id = 1
        data = {"secret_name": "Test edit"}
        response = await self.client.patch(f"/heroes/{hero_id}", json=data)
        self.assertEqual(HTTPStatus.OK, response.status_code)

        actual_data = response.json()
        hero = await Hero.get(Hero.id == hero_id)
        self.assertEqual(hero_id, hero.id)
        self.assertEqual(data["secret_name"], hero.secret_name)
        self.assertEqual(actual_data["secret_name"], data["secret_name"])
        self.assertEqual(actual_data["id"], hero_id)
