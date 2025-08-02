import asyncio
from http import HTTPStatus

from apps.authorization.models import Permission
from apps.user.models import User
from apps.user.utils.types import UserRole
from core.unittest.async_case import AsyncTestCase


class TestUserPermission(AsyncTestCase):
    fixtures = ["users"]

    async def async_set_up(self):
        await super().async_set_up()
        await Permission.generate_crud_objects(User.table_name())

        self.active, self.staff, self.admin = await asyncio.gather(
            User.get(role=UserRole.active),
            User.get(role=UserRole.staff),
            User.get(role=UserRole.admin),
        )

    async def test_get_user_permissions_not_found(self, app):
        await self.client.user_login(self.admin)

        response = await self.client.get(
            app.url_path_for("user-get-permissions", pk=-1)
        )
        assert HTTPStatus.NOT_FOUND == response.status_code
        assert response.json() == {"detail": "User not found."}

    async def test_get_another_user_permissions_denied(self, app):
        response = await self.client.get(
            app.url_path_for("user-get-permissions", pk=self.active.id)
        )
        assert HTTPStatus.UNAUTHORIZED == response.status_code

        await self.client.user_login(self.staff)

        response = await self.client.get(
            app.url_path_for("user-get-permissions", pk=self.active.id)
        )
        assert HTTPStatus.FORBIDDEN == response.status_code

    async def test_get_own_user_permissions_using_admin_endpoint_denied(self, app):
        response = await self.client.get(
            app.url_path_for("user-get-permissions", pk=self.staff.id)
        )
        assert HTTPStatus.UNAUTHORIZED == response.status_code

        await self.client.user_login(self.staff)

        expected_permissions = [
            Permission.format_permission_name("read", User.table_name()),
            Permission.format_permission_name("create", User.table_name()),
            Permission.format_permission_name("update", User.table_name()),
        ]
        await self.add_permissions(self.staff, expected_permissions)

        response = await self.client.get(
            app.url_path_for("user-get-permissions", pk=self.staff.id)
        )
        assert HTTPStatus.FORBIDDEN == response.status_code
        assert (
            "Insufficient rights to carry out this action" == response.json()["detail"]
        )

    async def test_get_own_user_permissions_allowed(self, app):
        response = await self.client.get(app.url_path_for("user-own-permissions"))
        assert HTTPStatus.UNAUTHORIZED == response.status_code

        await self.client.user_login(self.staff)

        expected_permissions = [
            Permission.format_permission_name("read", User.table_name()),
            Permission.format_permission_name("create", User.table_name()),
            Permission.format_permission_name("update", User.table_name()),
        ]
        await self.add_permissions(self.staff, expected_permissions)

        response = await self.client.get(app.url_path_for("user-own-permissions"))
        assert HTTPStatus.OK == response.status_code

        assert len(response.json()) >= len(expected_permissions)
        assert all(perm["name"] in expected_permissions for perm in response.json())

    async def test_admin_get_user_permissions_allowed(self, app):
        response = await self.client.get(
            app.url_path_for("user-get-permissions", pk=self.staff.id)
        )
        assert HTTPStatus.UNAUTHORIZED == response.status_code

        await self.client.user_login(self.admin)

        # Get permissions of active user
        expected_permissions = [
            Permission.format_permission_name("read", User.table_name()),
            Permission.format_permission_name("create", User.table_name()),
            Permission.format_permission_name("update", User.table_name()),
        ]
        await self.add_permissions(self.active, expected_permissions)

        response = await self.client.get(
            app.url_path_for("user-get-permissions", pk=self.active.id)
        )
        assert HTTPStatus.OK == response.status_code

        assert len(response.json()) >= len(expected_permissions)
        assert all(perm["name"] in expected_permissions for perm in response.json())

        # Get permissions of staff user
        await self.add_permissions(self.staff, expected_permissions)
        response = await self.client.get(
            app.url_path_for("user-get-permissions", pk=self.staff.id)
        )
        assert HTTPStatus.OK == response.status_code

        assert len(response.json()) >= len(expected_permissions)
        assert all(perm["name"] in expected_permissions for perm in response.json())

    async def test_add_permissions_to_user_not_found(self, app):
        data = {
            "permissions": [
                Permission.format_permission_name("create", User.table_name()),
                Permission.format_permission_name("read", User.table_name()),
            ]
        }
        await self.client.user_login(self.admin)

        response = await self.client.patch(
            app.url_path_for("user-add-permissions", pk=-1), json=data
        )
        assert HTTPStatus.NOT_FOUND == response.status_code
        assert response.json() == {"detail": "User not found."}

    async def test_add_permissions_to_user(self, app):
        user = await User(
            username="add_permission",
            first_name="Test",
            last_name="Pytest",
            password=(lambda: "test123")(),
        ).save()
        data = {
            "permissions": [
                Permission.format_permission_name("create", User.table_name()),
                Permission.format_permission_name("read", User.table_name()),
            ]
        }
        perms = await Permission.filter(name__in=data["permissions"])
        assert user.has_permissions(perms) is False

        await self.client.user_login(user)

        response = await self.client.patch(
            app.url_path_for("user-add-permissions", pk=user.id), json=data
        )
        assert HTTPStatus.FORBIDDEN == response.status_code

        await self.client.user_login(self.admin)
        response = await self.client.patch(
            app.url_path_for("user-add-permissions", pk=user.id), json=data
        )
        assert HTTPStatus.OK == response.status_code

        user = await user.refresh()
        assert user.has_permissions(perms)
        expected_perms_response = [perm.model_dump(mode="json") for perm in perms]
        assert response.json() == expected_perms_response

    async def test_remove_permissions_to_user_not_found(self, app):
        data = {
            "permissions": [
                Permission.format_permission_name("create", User.table_name()),
                Permission.format_permission_name("read", User.table_name()),
            ]
        }
        await self.client.user_login(self.admin)

        response = await self.client.patch(
            app.url_path_for("user-remove-permissions", pk=-1), json=data
        )
        assert HTTPStatus.NOT_FOUND == response.status_code
        assert response.json() == {"detail": "User not found."}

    async def test_remove_permissions_to_user(self, app):
        data = {
            "permissions": [
                Permission.format_permission_name("create", User.table_name()),
                Permission.format_permission_name("read", User.table_name()),
            ]
        }
        user = await User(
            username="remove_permission",
            first_name="Test",
            last_name="Pytest",
            password=(lambda: "test123")(),
        ).save()

        await self.add_permissions(user, data["permissions"])
        perms = await Permission.filter(name__in=data["permissions"])
        assert user.has_permissions(perms)

        await self.client.user_login(user)

        response = await self.client.patch(
            app.url_path_for("user-remove-permissions", pk=user.id), json=data
        )
        assert HTTPStatus.FORBIDDEN == response.status_code

        await self.client.user_login(self.admin)
        response = await self.client.patch(
            app.url_path_for("user-remove-permissions", pk=user.id), json=data
        )
        assert HTTPStatus.OK == response.status_code

        user = await user.refresh()
        assert user.has_permissions(perms) is False
        perm_names = [perm["name"] for perm in response.json()]
        assert perm_names == data["permissions"]
