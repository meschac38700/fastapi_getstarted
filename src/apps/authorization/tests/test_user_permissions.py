from http import HTTPStatus

from apps.authorization.models import Permission
from apps.hero.models import Hero
from apps.user.models import User
from core.unittest.async_case import AsyncTestCase


class TestUserPermission(AsyncTestCase):
    fixtures = [
        "users",
        "heroes",
    ]

    async def async_set_up(self):
        await super().async_set_up()
        self.user = await User.get(username="test")
        await Permission.generate_crud_objects(Hero.table_name())

    async def test_user_has_no_rights_to_edit_resource(self, app):
        hero_id = 1
        await self.client.user_login(self.user)

        data = {"secret_name": "test edit"}
        response = await self.client.patch(
            app.url_path_for("hero-patch", pk=hero_id), json=data
        )
        assert HTTPStatus.FORBIDDEN == response.status_code
        assert (
            response.json()["detail"]
            == "You do not have sufficient rights to this resource."
        )

    async def test_user_has_rights_to_edit_resource(self, app):
        hero_id = 1
        await self.client.user_login(self.user)
        update_permission_name = Permission.format_permission_name(
            "update", Hero.table_name()
        )
        await self.add_permissions(self.user, [update_permission_name])

        data = {"secret_name": "test edit"}
        response = await self.client.patch(
            app.url_path_for("hero-patch", pk=hero_id), json=data
        )
        assert HTTPStatus.OK == response.status_code

        actual_data = response.json()
        hero = await Hero.get(id=hero_id)
        assert hero_id == hero.id
        assert data["secret_name"] == hero.secret_name
        assert actual_data["secret_name"] == data["secret_name"]
        assert actual_data["id"] == hero_id
