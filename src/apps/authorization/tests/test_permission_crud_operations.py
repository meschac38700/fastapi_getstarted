import asyncio
from http import HTTPStatus

from apps.authorization.models import Permission
from apps.user.models import User
from apps.user.utils.types import UserRole
from core.unittest.async_case import AsyncTestCase


class TestPermissionCRUD(AsyncTestCase):
    fixtures = [
        "users",
    ]

    async def async_set_up(self):
        await super().async_set_up()

        await Permission.generate_crud_objects(Permission.table_name())
        self.admin, self.staff = await asyncio.gather(
            User.get(role=UserRole.admin), User.get(role=UserRole.staff)
        )

    async def test_get_permission_with_staff_user_permission_denied(self, app):
        await self.client.user_login(self.staff)

        response = await self.client.get(app.url_path_for("permission-list"))
        assert HTTPStatus.FORBIDDEN == response.status_code
        assert (
            "Insufficient rights to carry out this action" == response.json()["detail"]
        )

    async def test_get_permission_with_admin_user(self, app):
        await self.client.user_login(self.admin)

        response = await self.client.get(app.url_path_for("permission-list"))
        assert HTTPStatus.OK == response.status_code
        assert len(response.json()) >= 4

    async def test_get_permission_filter_by_name(self, app):
        await self.client.user_login(self.admin)
        read_permission_name = Permission.format_permission_name(
            "read", Permission.table_name()
        )
        response = await self.client.get(
            app.url_path_for("permission-list"), params={"name": read_permission_name}
        )
        assert HTTPStatus.OK == response.status_code
        expected = {
            "name": read_permission_name,
            "target_table": Permission.table_name(),
            "display_name": "Read permission",
            "description": "This permission allows user to read the Permission model.",
            "created_at": response.json()[0]["created_at"],
            "updated_at": None,
        }
        data = response.json()
        assert len(data) == 1
        actual = data[0]
        actual.pop("id", None)
        assert actual == expected

    async def test_get_permission_filter_by_target_table(self, app):
        await self.client.user_login(self.admin)

        response = await self.client.get(
            app.url_path_for("permission-list"),
            params={"target_table": Permission.table_name()},
        )
        assert HTTPStatus.OK == response.status_code
        assert len(response.json()) >= 4

    async def test_get_permission_filter_by_name_and_target_table(self, app):
        await self.client.user_login(self.admin)
        create_permission_name = Permission.format_permission_name(
            "create", Permission.table_name()
        )
        response = await self.client.get(
            app.url_path_for("permission-list"),
            params={
                "name": create_permission_name,
                "target_table": Permission.table_name(),
            },
        )
        assert HTTPStatus.OK == response.status_code
        expected = {
            "name": create_permission_name,
            "target_table": Permission.table_name(),
            "display_name": "Create permission",
            "description": "This permission allows user to create the Permission model.",
            "created_at": response.json()[0]["created_at"],
            "updated_at": None,
        }
        data = response.json()
        assert len(data) == 1
        actual = data[0]
        actual.pop("id", None)
        assert actual == expected

    async def test_add_new_permission(self, app):
        post_data = {
            "name": "delete_admin_account",
            "target_table": User.table_name(),
            "display_name": "Delete admin account",
        }
        response = await self.client.post(
            app.url_path_for("permission-create"), json=post_data
        )
        assert HTTPStatus.UNAUTHORIZED == response.status_code

        await self.client.user_login(self.staff)

        response = await self.client.post(
            app.url_path_for("permission-create"), json=post_data
        )
        assert HTTPStatus.FORBIDDEN == response.status_code

        await self.client.force_login(self.admin)

        response = await self.client.post(
            app.url_path_for("permission-create"), json=post_data
        )
        assert HTTPStatus.CREATED == response.status_code

        actual_data = response.json()
        created_permission_id = actual_data.pop("id", None)
        assert created_permission_id is not None
        assert await Permission.get(id=created_permission_id) is not None
        assert all(actual_data[k] == v for k, v in post_data.items())

    async def test_patch_permission_not_found(self, app):
        await self.client.user_login(self.admin)
        update_data = {
            "description": "New permission description",
            "display_name": "Delete admin account Modified",
        }
        permission_id = -1
        response = await self.client.patch(
            app.url_path_for("permission-patch", pk=permission_id), json=update_data
        )
        assert HTTPStatus.NOT_FOUND == response.status_code
        assert response.json() == {"detail": "Permission not found."}

    async def test_using_patch_instead_of_put(self, app):
        await self.client.user_login(self.admin)
        update_data = {
            "name": "modify_admin_account",
            "target_table": Permission.table_name(),
            "description": "New permission description",
            "display_name": "Delete admin account Modified",
        }
        _permission = await Permission(
            name="patch_test_permission_instead_of_put",
            target_table=Permission.table_name(),
        ).save()
        response = await self.client.patch(
            app.url_path_for("permission-patch", pk=_permission.id), json=update_data
        )
        assert HTTPStatus.BAD_REQUEST == response.status_code
        assert response.json() == {
            "detail": "Cannot use PATCH to update entire registry, use PUT instead."
        }

    async def test_patch_permission(self, app):
        update_data = {
            "description": "New permission description",
            "display_name": "Delete admin account Modified",
        }
        permission = await Permission(
            name="patch_test_permission", target_table=Permission.table_name()
        ).save()
        response = await self.client.patch(
            app.url_path_for("permission-patch", pk=permission.id), json=update_data
        )
        assert HTTPStatus.UNAUTHORIZED == response.status_code

        await self.client.user_login(self.staff)

        response = await self.client.patch(
            app.url_path_for("permission-patch", pk=permission.id), json=update_data
        )
        assert HTTPStatus.FORBIDDEN == response.status_code

        await self.client.force_login(self.admin)

        response = await self.client.patch(
            app.url_path_for("permission-patch", pk=permission.id), json=update_data
        )
        assert HTTPStatus.OK == response.status_code

        actual_data = response.json()
        assert actual_data.pop("id", None) is not None
        assert all(actual_data[k] == v for k, v in update_data.items())

    async def test_put_permission(self, app):
        update_data = {
            "name": "update_test_permission_modified",
            "target_table": "permission_test",
        }
        permission = await Permission(
            name="update_test_permission", target_table=Permission.table_name()
        ).save()
        response = await self.client.put(
            app.url_path_for("permission-update", pk=permission.id), json=update_data
        )
        assert HTTPStatus.UNAUTHORIZED == response.status_code

        await self.client.user_login(self.staff)

        response = await self.client.put(
            app.url_path_for("permission-update", pk=permission.id), json=update_data
        )
        assert HTTPStatus.FORBIDDEN == response.status_code

        await self.client.force_login(self.admin)

        response = await self.client.put(
            app.url_path_for("permission-update", pk=permission.id), json=update_data
        )
        assert HTTPStatus.OK == response.status_code

        actual_data = response.json()
        assert actual_data.pop("id", None) is not None
        assert all(actual_data[k] == v for k, v in update_data.items())

    async def test_delete_permission(self, app):
        permission = await Permission(
            name="delete_test_permission", target_table=Permission.table_name()
        ).save()
        response = await self.client.delete(
            app.url_path_for("permission-delete", pk=permission.id),
        )
        assert HTTPStatus.UNAUTHORIZED == response.status_code

        await self.client.user_login(self.staff)

        response = await self.client.delete(
            app.url_path_for("permission-delete", pk=permission.id),
        )
        assert HTTPStatus.FORBIDDEN == response.status_code

        await self.client.force_login(self.admin)

        response = await self.client.delete(
            app.url_path_for("permission-delete", pk=permission.id),
        )
        assert HTTPStatus.NO_CONTENT == response.status_code

        assert await Permission.get(id=permission.id) is None
