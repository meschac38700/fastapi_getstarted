import asyncio
from http import HTTPStatus

from apps.authorization.models.permission import Permission
from apps.user.models import User
from apps.user.utils.types import UserRole
from core.test.async_case import AsyncTestCase


class TestPermissionCRUD(AsyncTestCase):
    fixtures = [
        "users",
    ]

    async def asyncSetUp(self):
        await super().asyncSetUp()

        await Permission.generate_crud_objects(Permission.table_name())
        self.admin, self.staff = await asyncio.gather(
            User.get(User.role == UserRole.admin), User.get(User.role == UserRole.staff)
        )

    async def test_get_permission_with_staff_user_permission_denied(self):
        await self.client.user_login(self.staff)

        response = await self.client.get("authorizations/permissions")
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)
        self.assertEqual(
            "Your role does not allow you to do this action",
            response.json()["detail"],
        )

    async def test_get_permission_with_admin_user(self):
        await self.client.user_login(self.admin)

        response = await self.client.get("authorizations/permissions")
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertTrue(len(response.json()) >= 4)

    async def test_get_permission_filter_by_name(self):
        await self.client.user_login(self.admin)

        response = await self.client.get(
            "authorizations/permissions", params={"name": "read_permission"}
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)
        expected = {
            "name": "read_permission",
            "target_table": "permission",
            "display_name": "Read permission",
            "description": "This permission allows user to read any Permission instance.",
        }
        data = response.json()
        self.assertTrue(len(data) == 1)
        actual = data[0]
        actual.pop("id", None)
        self.assertEqual(actual, expected)

    async def test_get_permission_filter_by_target_table(self):
        await self.client.user_login(self.admin)

        response = await self.client.get(
            "authorizations/permissions", params={"target_table": "permission"}
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertTrue(len(response.json()) >= 4)

    async def test_get_permission_filter_by_name_and_target_table(self):
        await self.client.user_login(self.admin)

        response = await self.client.get(
            "authorizations/permissions",
            params={"name": "create_permission", "target_table": "permission"},
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)
        expected = {
            "name": "create_permission",
            "target_table": "permission",
            "display_name": "Create permission",
            "description": "This permission allows user to create any Permission instance.",
        }
        data = response.json()
        self.assertTrue(len(data) == 1)
        actual = data[0]
        actual.pop("id", None)
        self.assertEqual(actual, expected)
