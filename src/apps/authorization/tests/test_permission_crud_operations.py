import asyncio
from http import HTTPStatus

from apps.authorization.models import Permission
from apps.user.models import User
from apps.user.utils.types import UserRole
from core.testing.async_case import AsyncTestCase


class TestPermissionCRUD(AsyncTestCase):
    fixtures = [
        "users",
    ]

    async def asyncSetUp(self):
        await super().asyncSetUp()

        await Permission.generate_crud_objects(Permission.table_name())
        self.admin, self.staff = await asyncio.gather(
            User.get(role=UserRole.admin), User.get(role=UserRole.staff)
        )

    async def test_get_permission_with_staff_user_permission_denied(self):
        await self.client.user_login(self.staff)

        response = await self.client.get("authorizations/permissions/")
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)
        self.assertEqual(
            "this action is prohibited with this user currently logged in",
            response.json()["detail"],
        )

    async def test_get_permission_with_admin_user(self):
        await self.client.user_login(self.admin)

        response = await self.client.get("authorizations/permissions/")
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertTrue(len(response.json()) >= 4)

    async def test_get_permission_filter_by_name(self):
        await self.client.user_login(self.admin)

        response = await self.client.get(
            "authorizations/permissions/", params={"name": "read_permission"}
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)
        expected = {
            "name": "read_permission",
            "target_table": "permission",
            "display_name": "Read permission",
            "description": "This permission allows user to read the Permission model.",
        }
        data = response.json()
        self.assertTrue(len(data) == 1)
        actual = data[0]
        actual.pop("id", None)
        self.assertEqual(actual, expected)

    async def test_get_permission_filter_by_target_table(self):
        await self.client.user_login(self.admin)

        response = await self.client.get(
            "authorizations/permissions/", params={"target_table": "permission"}
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertTrue(len(response.json()) >= 4)

    async def test_get_permission_filter_by_name_and_target_table(self):
        await self.client.user_login(self.admin)

        response = await self.client.get(
            "authorizations/permissions/",
            params={"name": "create_permission", "target_table": "permission"},
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)
        expected = {
            "name": "create_permission",
            "target_table": "permission",
            "display_name": "Create permission",
            "description": "This permission allows user to create the Permission model.",
        }
        data = response.json()
        self.assertTrue(len(data) == 1)
        actual = data[0]
        actual.pop("id", None)
        self.assertEqual(actual, expected)

    async def test_add_new_permission(self):
        post_data = {
            "name": "delete_admin_account",
            "target_table": "user",
            "display_name": "Delete admin account",
        }
        response = await self.client.post(
            "/authorizations/permissions/", json=post_data
        )
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)

        await self.client.user_login(self.staff)

        response = await self.client.post(
            "/authorizations/permissions/", json=post_data
        )
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)

        await self.client.force_login(self.admin)

        response = await self.client.post(
            "/authorizations/permissions/", json=post_data
        )
        self.assertEqual(HTTPStatus.CREATED, response.status_code)

        actual_data = response.json()
        created_permission_id = actual_data.pop("id", None)
        self.assertIsNotNone(created_permission_id)
        self.assertIsNotNone(await Permission.get(id=created_permission_id))
        self.assertTrue(actual_data[k] == v for k, v in post_data.items())

    async def test_patch_permission(self):
        update_data = {
            "description": "New permission description",
            "display_name": "Delete admin account Modified",
        }
        permission = await Permission(
            name="patch_test_permission", target_table=Permission.table_name()
        ).save()
        response = await self.client.patch(
            f"/authorizations/permissions/{permission.id}/", json=update_data
        )
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)

        await self.client.user_login(self.staff)

        response = await self.client.patch(
            f"/authorizations/permissions/{permission.id}/", json=update_data
        )
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)

        await self.client.force_login(self.admin)

        response = await self.client.patch(
            f"/authorizations/permissions/{permission.id}/", json=update_data
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)

        actual_data = response.json()
        self.assertIsNotNone(actual_data.pop("id", None))
        self.assertTrue(actual_data[k] == v for k, v in update_data.items())

    async def test_put_permission(self):
        update_data = {
            "name": "update_test_permission_modified",
            "target_table": "permission_test",
        }
        permission = await Permission(
            name="update_test_permission", target_table=Permission.table_name()
        ).save()
        response = await self.client.put(
            f"/authorizations/permissions/{permission.id}/", json=update_data
        )
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)

        await self.client.user_login(self.staff)

        response = await self.client.put(
            f"/authorizations/permissions/{permission.id}/", json=update_data
        )
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)

        await self.client.force_login(self.admin)

        response = await self.client.put(
            f"/authorizations/permissions/{permission.id}/", json=update_data
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)

        actual_data = response.json()
        self.assertIsNotNone(actual_data.pop("id", None))
        self.assertTrue(actual_data[k] == v for k, v in update_data.items())

    async def test_delete_permission(self):
        permission = await Permission(
            name="delete_test_permission", target_table=Permission.table_name()
        ).save()
        response = await self.client.delete(
            f"/authorizations/permissions/{permission.id}/"
        )
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)

        await self.client.user_login(self.staff)

        response = await self.client.delete(
            f"/authorizations/permissions/{permission.id}/"
        )
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)

        await self.client.force_login(self.admin)

        response = await self.client.delete(
            f"/authorizations/permissions/{permission.id}/"
        )
        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)

        self.assertIsNone(await Permission.get(id=permission.id))
