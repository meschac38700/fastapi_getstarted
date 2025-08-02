import asyncio
from http import HTTPStatus

from apps.authorization.models import Permission
from apps.user.models import User
from apps.user.utils.types import UserRole
from core.unittest.async_case import AsyncTestCase


class TestUserRoles(AsyncTestCase):
    fixtures = [
        "users",
    ]

    async def async_set_up(self):
        await super().async_set_up()
        _, self.admin, self.staff, self.active = await asyncio.gather(
            Permission.generate_crud_objects(User.table_name()),
            User.get(role=UserRole.admin),
            User.get(role=UserRole.staff),
            User.get(role=UserRole.active),
        )
        assert self.staff is not None
        assert self.admin is not None
        assert self.active is not None

    async def test_user_active_can_delete_only_his_own_account(self, app):
        assert self.active is not None
        delete_perm = Permission.format_permission_name("delete", User.table_name())
        await self.add_permissions(self.active, [delete_perm])
        await self.client.user_login(self.active)

        # Try to delete another account than his own
        response = await self.client.delete(
            app.url_path_for("user-delete", pk=self.admin.id)
        )
        assert HTTPStatus.FORBIDDEN == response.status_code
        assert (
            "Insufficient rights to carry out this action" == response.json()["detail"]
        )

        response = await self.client.delete(
            app.url_path_for("user-delete", pk=self.active.id)
        )
        assert HTTPStatus.NO_CONTENT == response.status_code
        assert await User.get(id=self.active.id) is None

    async def test_user_staff_can_delete_only_his_own_account(self, app):
        delete_perm = Permission.format_permission_name("delete", User.table_name())
        await self.add_permissions(self.staff, [delete_perm])
        await self.client.user_login(self.staff)

        # Try to delete another account than his own
        user = await User(
            username="someone",
            first_name="John",
            last_name="DOE",
            password=(lambda: "someone")(),
        ).save()
        response = await self.client.delete(app.url_path_for("user-delete", pk=user.id))
        assert HTTPStatus.FORBIDDEN == response.status_code
        assert (
            "Insufficient rights to carry out this action" == response.json()["detail"]
        )

        # Delete his own account: Should pass
        response = await self.client.delete(
            app.url_path_for("user-delete", pk=self.staff.id)
        )
        assert HTTPStatus.NO_CONTENT == response.status_code
        assert await User.get(id=self.staff.id) is None

    async def test_user_admin_can_delete_any_account(self, app):
        user = await User(
            username="someone",
            first_name="John",
            last_name="DOE",
            password=(lambda: "someone")(),
        ).save()
        assert self.admin is not None
        delete_perm = Permission.format_permission_name("delete", User.table_name())
        await self.add_permissions(self.admin, [delete_perm])
        await self.client.user_login(self.admin)

        # Try to delete another account than his own
        response = await self.client.delete(app.url_path_for("user-delete", pk=user.id))
        assert HTTPStatus.NO_CONTENT == response.status_code
        assert await User.get(id=user.id) is None

        # Delete his own account: Should pass
        response = await self.client.delete(
            app.url_path_for("user-delete", pk=self.admin.id)
        )
        assert HTTPStatus.NO_CONTENT == response.status_code
        assert await User.get(id=self.admin.id) is None

    async def test_user_active_cannot_update_role_field(self, app):
        update_data = {
            "username": "jean",
            "first_name": "Jean",
            "last_name": "DUPONT",
            "password": (lambda: "jean")(),
            "role": "admin",
        }
        update_perm = Permission.format_permission_name("update", User.table_name())
        await self.add_permissions(self.active, [update_perm])
        await self.client.user_login(self.active)

        response = await self.client.put(
            app.url_path_for("user-update", pk=self.active.id), json=update_data
        )
        assert HTTPStatus.OK == response.status_code

        assert UserRole.active.value == response.json()["role"]
        await self.active.refresh()
        assert UserRole.active == self.active.role

    async def test_user_active_cannot_patch_role_field(self, app):
        update_data = {"role": "admin"}
        update_perm = Permission.format_permission_name("update", User.table_name())
        await self.add_permissions(self.active, [update_perm])
        await self.client.user_login(self.active)

        response = await self.client.patch(
            app.url_path_for("user-patch", pk=self.active.id), json=update_data
        )
        assert HTTPStatus.OK == response.status_code

        assert UserRole.active.value, response.json()["role"]
        await self.active.refresh()
        assert UserRole.active == self.active.role

    async def test_user_staff_cannot_update_role_field(self, app):
        update_data = {
            "username": "jean",
            "first_name": "Jean",
            "last_name": "DUPONT",
            "password": (lambda: "jean")(),
            "role": "admin",
        }
        update_perm = Permission.format_permission_name("update", User.table_name())
        await self.add_permissions(self.active, [update_perm])
        await self.client.user_login(self.staff)

        response = await self.client.put(
            app.url_path_for("user-update", pk=self.staff.id), json=update_data
        )
        assert HTTPStatus.FORBIDDEN == response.status_code

        assert "role" not in response.json()
        await self.staff.refresh()
        assert UserRole.staff == self.staff.role

    async def test_user_staff_cannot_patch_role_field(self, app):
        update_data = {"role": "admin"}
        update_perm = Permission.format_permission_name("update", User.table_name())
        await self.add_permissions(self.active, [update_perm])
        await self.client.user_login(self.staff)

        response = await self.client.patch(
            app.url_path_for("user-patch", pk=self.staff.id), json=update_data
        )
        assert HTTPStatus.FORBIDDEN == response.status_code

        assert "role" not in response.json()
        await self.staff.refresh()
        assert UserRole.staff == self.staff.role

    async def test_user_admin_can_update_role_field(self, app):
        update_data = {
            "username": "jean_admin",
            "first_name": "Jean",
            "last_name": "DUPONT",
            "password": (lambda: "jean")(),
            "role": "admin",
        }
        await self.client.user_login(self.admin)

        response = await self.client.put(
            app.url_path_for("user-update", pk=self.staff.id), json=update_data
        )
        assert HTTPStatus.OK == response.status_code

        assert UserRole.admin.value == response.json()["role"]
        await self.staff.refresh()
        assert UserRole.admin == self.staff.role
        self.staff.role = UserRole.staff
        await self.staff.save()
        assert UserRole.staff == self.staff.role

    async def test_user_admin_can_patch_role_field(self, app):
        update_data = {"role": "admin"}
        await self.client.user_login(self.admin)

        response = await self.client.patch(
            app.url_path_for("user-patch", pk=self.staff.id), json=update_data
        )
        assert HTTPStatus.OK == response.status_code

        assert UserRole.admin.value == response.json()["role"]
        await self.staff.refresh()
        assert UserRole.admin == self.staff.role
        self.staff.role = UserRole.staff
        await self.staff.save()
        assert UserRole.staff == self.staff.role
