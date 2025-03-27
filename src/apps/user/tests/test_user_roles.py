import asyncio
from http import HTTPStatus

from apps.authorization.models import Permission
from apps.user.models import User
from apps.user.utils.types import UserRole
from core.testing.async_case import AsyncTestCase


class TestUserRoles(AsyncTestCase):
    fixtures = [
        "users",
    ]

    async def asyncSetUp(self):
        await super().asyncSetUp()
        _, self.admin, self.staff, self.active = await asyncio.gather(
            Permission.generate_crud_objects(User.table_name()),
            User.get(role=UserRole.admin),
            User.get(role=UserRole.staff),
            User.get(role=UserRole.active),
        )

    async def test_user_active_can_delete_only_his_own_account(self):
        self.assertIsNotNone(self.active)
        await self.add_permissions(self.active, ["delete_user"])
        await self.client.user_login(self.active)

        # Try to delete another account than his own
        response = await self.client.delete(f"/users/{self.admin.id}/")
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)
        self.assertEqual(
            "this action is prohibited with this user currently logged in",
            response.json()["detail"],
        )

        # Delete his own account: Should pass
        response = await self.client.delete(f"/users/{self.active.id}/")
        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)
        self.assertIsNone(await User.get(id=self.active.id))

    async def test_user_staff_can_delete_only_his_own_account(self):
        await self.add_permissions(self.staff, ["delete_user"])
        await self.client.user_login(self.staff)

        # Try to delete another account than his own
        user = await User(
            username="someone", first_name="John", last_name="DOE", password="someone"
        ).save()
        response = await self.client.delete(f"/users/{user.id}/")
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)
        self.assertEqual(
            "this action is prohibited with this user currently logged in",
            response.json()["detail"],
        )

        # Delete his own account: Should pass
        response = await self.client.delete(f"/users/{self.staff.id}/")
        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)
        self.assertIsNone(await User.get(id=self.staff.id))

    async def test_user_admin_can_delete_any_account(self):
        user = await User(
            username="someone", first_name="John", last_name="DOE", password="someone"
        ).save()
        self.assertIsNotNone(self.admin)
        await self.add_permissions(self.admin, ["delete_user"])
        await self.client.user_login(self.admin)

        # Try to delete another account than his own
        response = await self.client.delete(f"/users/{user.id}/")
        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)
        self.assertIsNone(await User.get(id=user.id))

        # Delete his own account: Should pass
        response = await self.client.delete(f"/users/{self.admin.id}/")
        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)
        self.assertIsNone(await User.get(id=self.admin.id))

    async def test_user_active_cannot_update_role_field(self):
        update_data = {
            "username": "jean",
            "first_name": "Jean",
            "last_name": "DUPONT",
            "password": "jean",
            "role": "admin",
        }
        await self.active.add_permission(await Permission.get(name="update_user"))
        await self.client.user_login(self.active)

        response = await self.client.put(f"/users/{self.active.id}/", json=update_data)
        self.assertEqual(HTTPStatus.OK, response.status_code)

        self.assertEqual(UserRole.active.value, response.json()["role"])
        await self.active.refresh()
        self.assertEqual(UserRole.active, self.active.role)

    async def test_user_active_cannot_patch_role_field(self):
        update_data = {"role": "admin"}
        await self.active.add_permission(await Permission.get(name="update_user"))
        await self.client.user_login(self.active)

        response = await self.client.patch(
            f"/users/{self.active.id}/", json=update_data
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)

        self.assertEqual(UserRole.active.value, response.json()["role"])
        await self.active.refresh()
        self.assertEqual(UserRole.active, self.active.role)

    async def test_user_staff_cannot_update_role_field(self):
        update_data = {
            "username": "jean",
            "first_name": "Jean",
            "last_name": "DUPONT",
            "password": "jean",
            "role": "admin",
        }
        await self.staff.add_permission(await Permission.get(name="update_user"))
        await self.client.user_login(self.staff)

        response = await self.client.put(f"/users/{self.staff.id}/", json=update_data)
        self.assertEqual(HTTPStatus.OK, response.status_code)

        self.assertEqual(UserRole.staff.value, response.json()["role"])
        await self.staff.refresh()
        self.assertEqual(UserRole.staff, self.staff.role)

    async def test_user_staff_cannot_patch_role_field(self):
        update_data = {"role": "admin"}
        await self.staff.add_permission(await Permission.get(name="update_user"))
        await self.client.user_login(self.staff)

        response = await self.client.patch(f"/users/{self.staff.id}/", json=update_data)
        self.assertEqual(HTTPStatus.OK, response.status_code)

        self.assertEqual(UserRole.staff.value, response.json()["role"])
        await self.staff.refresh()
        self.assertEqual(UserRole.staff, self.staff.role)

    async def test_user_admin_can_update_role_field(self):
        update_data = {
            "username": "jean",
            "first_name": "Jean",
            "last_name": "DUPONT",
            "password": "jean",
            "role": "admin",
        }
        await self.client.user_login(self.admin)

        response = await self.client.put(f"/users/{self.staff.id}/", json=update_data)
        self.assertEqual(HTTPStatus.OK, response.status_code)

        self.assertEqual(UserRole.admin.value, response.json()["role"])
        await self.staff.refresh()
        self.assertEqual(UserRole.admin, self.staff.role)

    async def test_user_admin_can_patch_role_field(self):
        update_data = {"role": "admin"}
        await self.client.user_login(self.admin)

        response = await self.client.patch(f"/users/{self.staff.id}/", json=update_data)
        self.assertEqual(HTTPStatus.OK, response.status_code)

        self.assertEqual(UserRole.admin.value, response.json()["role"])
        await self.staff.refresh()
        self.assertEqual(UserRole.admin, self.staff.role)
