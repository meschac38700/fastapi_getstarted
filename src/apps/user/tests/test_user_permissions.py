import asyncio
from http import HTTPStatus

from apps.authorization.models.permission import Permission
from apps.user.models import User
from apps.user.utils.types import UserRole
from core.test.async_case import AsyncTestCase


class TestUserPermission(AsyncTestCase):
    fixtures = ["users"]

    async def asyncSetUp(self):
        await super().asyncSetUp()
        await Permission.generate_crud_objects(User.table_name())

        self.active, self.staff, self.admin = await asyncio.gather(
            User.get(User.role == UserRole.active),
            User.get(User.role == UserRole.staff),
            User.get(User.role == UserRole.admin),
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
            "this action is prohibited with this user currently logged in",
            response.json()["detail"],
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

    async def test_add_permissions_to_user(self):
        user = await User(
            username="add_permission",
            first_name="Test",
            last_name="Pytest",
            password="test123",
        ).save()
        data = {"permissions": ["create_user", "read_user"]}
        perms = await Permission.filter(Permission.name.in_(data["permissions"]))
        self.assertFalse(user.has_permissions(perms))

        await self.client.user_login(user)

        response = await self.client.post(
            f"/users/{user.id}/permissions/add/", json=data
        )
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)

        await self.client.user_login(self.admin)
        response = await self.client.post(
            f"/users/{user.id}/permissions/add/", json=data
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)

        user = await user.refresh()
        self.assertTrue(user.has_permissions(perms))
        expected_perms_response = [perm.model_dump(mode="json") for perm in perms]
        self.assertEqual(response.json(), expected_perms_response)

    async def test_remove_permissions_to_user(self):
        data = {"permissions": ["create_user", "read_user"]}
        user = await User(
            username="remove_permission",
            first_name="Test",
            last_name="Pytest",
            password="test123",
        ).save()

        await self.add_permissions(user, data["permissions"])
        perms = await Permission.filter(Permission.name.in_(data["permissions"]))
        self.assertTrue(user.has_permissions(perms))

        await self.client.user_login(user)

        response = await self.client.post(
            f"/users/{user.id}/permissions/remove/", json=data
        )
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)

        await self.client.user_login(self.admin)
        response = await self.client.post(
            f"/users/{user.id}/permissions/remove/", json=data
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)

        user = await user.refresh()
        self.assertFalse(user.has_permissions(perms))
        self.assertListEqual(response.json(), [])
