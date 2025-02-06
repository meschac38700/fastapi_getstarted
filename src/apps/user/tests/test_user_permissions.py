import asyncio
from http import HTTPStatus

from apps.authorization.models.permission import Permission
from apps.user.models import User
from core.test.async_case import AsyncTestCase


class TestUserPermission(AsyncTestCase):
    fixtures = ["users"]

    async def asyncSetUp(self):
        await super().asyncSetUp()
        await Permission.generate_crud_objects(User.table_name())

        self.active, self.staff, self.admin = await asyncio.gather(
            User.get(User.role == "active"),
            User.get(User.role == "staff"),
            User.get(User.role == "admin"),
        )

    async def test_get_another_user_permissions_denied(self):
        response = await self.client.get("/users/permissions/")
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)

        await self.client.user_login(self.staff)

        response = await self.client.get(f"/users/{self.active.id}/permissions/")
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)

    async def test_get_own_user_permissions_using_admin_endpoint_denied(self):
        response = await self.client.get(f"/users/{self.staff.id}/permissions/")
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)

        await self.client.user_login(self.staff)

        expected_permissions = ["read_user", "create_user", "update_user"]
        await self.add_permissions(self.staff, expected_permissions)

        response = await self.client.get(f"/users/{self.staff.id}/permissions/")
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)
        self.assertEqual(
            "Your role does not allow you to do this action", response.json()["detail"]
        )

    async def test_get_own_user_permissions_denied(self):
        response = await self.client.get("/users/permissions/")
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)

        await self.client.user_login(self.staff)

        expected_permissions = ["read_user", "create_user", "update_user"]
        await self.add_permissions(self.staff, expected_permissions)

        response = await self.client.get("/users/permissions/")
        self.assertEqual(HTTPStatus.OK, response.status_code)

        self.assertTrue(len(response.json()) >= len(expected_permissions))
        self.assertTrue(
            all(perm["name"] in expected_permissions for perm in response.json())
        )

    async def test_admin_get_user_permissions_denied(self):
        response = await self.client.get(f"/users/{self.staff.id}/permissions/")
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)

        await self.client.user_login(self.admin)

        # Get permissions of active user
        expected_permissions = ["read_user", "create_user", "update_user"]
        await self.add_permissions(self.active, expected_permissions)

        response = await self.client.get(f"/users/{self.active.id}/permissions/")
        self.assertEqual(HTTPStatus.OK, response.status_code)

        self.assertTrue(len(response.json()) >= len(expected_permissions))
        self.assertTrue(
            all(perm["name"] in expected_permissions for perm in response.json())
        )

        # Get permissions of staff user
        await self.add_permissions(self.staff, expected_permissions)
        response = await self.client.get(f"/users/{self.staff.id}/permissions/")
        self.assertEqual(HTTPStatus.OK, response.status_code)

        self.assertTrue(len(response.json()) >= len(expected_permissions))
        self.assertTrue(
            all(perm["name"] in expected_permissions for perm in response.json())
        )
