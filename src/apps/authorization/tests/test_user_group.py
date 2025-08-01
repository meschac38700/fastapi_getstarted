from http import HTTPStatus

from apps.authorization.models import Group
from apps.user.models import User
from apps.user.utils.types import UserRole
from core.unittest.async_case import AsyncTestCase


class TestUserGroup(AsyncTestCase):
    fixtures = ["users"]

    async def async_set_up(self):
        await super().async_set_up()
        self.admin = await User.get(role=UserRole.admin)
        self.staff = await User.get(role=UserRole.staff)
        self.active = await User.get(role=UserRole.active)

    async def test_add_users_to_group(self, app):
        group = await Group(
            name="active_users",
            target_table=User.table_name(),
            display_name="Group of active users",
        ).save()
        assert group.users == []

        data = {
            "users": [self.active.username, self.staff.username, self.admin.username]
        }
        await self.client.user_login(self.staff)
        response = await self.client.patch(
            app.url_path_for("group-add-user", pk=group.id), json=data
        )
        assert HTTPStatus.FORBIDDEN == response.status_code

        await self.client.user_login(self.admin)
        response = await self.client.patch(
            app.url_path_for("group-add-user", pk=group.id), json=data
        )

        assert HTTPStatus.OK == response.status_code
        expected_response = [
            self.admin.model_dump(mode="json"),
            self.staff.model_dump(mode="json"),
            self.active.model_dump(mode="json"),
        ]
        assert response.json() == expected_response

    async def test_remove_users_to_group(self, app):
        group_admin = await Group(
            name="administrators",
            target_table="test",
            display_name="Only for admin users.",
        ).save()
        assert group_admin.users == []
        users = await User.all()
        await group_admin.extend_users(users)
        assert group_admin.users == users
        data = {
            "users": [
                self.active.username,
                self.staff.username,
            ]
        }
        await self.client.user_login(self.staff)
        response = await self.client.patch(
            app.url_path_for("group-remove-user", pk=group_admin.id), json=data
        )
        assert HTTPStatus.FORBIDDEN == response.status_code

        await self.client.user_login(self.admin)
        response = await self.client.patch(
            app.url_path_for("group-remove-user", pk=group_admin.id), json=data
        )
        assert HTTPStatus.OK == response.status_code
        expected_response = [
            self.admin.model_dump(mode="json"),
        ]
        assert response.json() == expected_response
        await group_admin.refresh()
        assert group_admin.users == [self.admin]
