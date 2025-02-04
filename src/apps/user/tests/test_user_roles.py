import asyncio
from http import HTTPStatus

from apps.authorization.models.permission import Permission
from apps.user.models import User
from apps.user.utils.types import UserRole
from core.test.async_case import AsyncTestCase


class TestUserRoles(AsyncTestCase):
    fixtures = [
        "users",
    ]

    async def asyncSetUp(self):
        await super().asyncSetUp()
        # TODO(Eliam): You already know the song. to be removed
        _, self.admin, self.staff, self.active = await asyncio.gather(
            Permission.generate_crud_objects(User.table_name()),
            User.get(User.role == UserRole.admin),
            User.get(User.role == UserRole.staff),
            User.get(User.role == UserRole.active),
        )

    async def test_user_active_can_delete_only_his_own_account(self):
        await self.add_permissions(self.active, ["delete_user"])
        await self.client.user_login(self.active)

        # Try to delete another account than his own
        response = await self.client.delete(f"/users/{self.admin.id}")
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)
        self.assertEqual(
            "You do not have sufficient rights to this resource.",
            response.json()["detail"],
        )

        # Delete his own account: Should pass
        response = await self.client.delete(f"/users/{self.active.id}")
        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)
        self.assertIsNone(await User.get(User.id == self.active.id))

    async def test_user_staff_can_delete_only_his_own_account(self):
        await self.add_permissions(self.staff, ["delete_user"])
        await self.client.user_login(self.staff)

        # Try to delete another account than his own
        response = await self.client.delete(f"/users/{self.admin.id}")
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)
        self.assertEqual(
            "You do not have sufficient rights to this resource.",
            response.json()["detail"],
        )

        # Delete his own account: Should pass
        response = await self.client.delete(f"/users/{self.staff.id}")
        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)
        self.assertIsNone(await User.get(User.id == self.staff.id))

    async def test_user_admin_can_delete_any_account(self):
        await self.add_permissions(self.admin, ["delete_user"])
        await self.client.user_login(self.admin)

        # Try to delete another account than his own
        response = await self.client.delete(f"/users/{self.staff.id}")
        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)
        self.assertIsNone(await User.get(User.id == self.staff.id))

        # Delete his own account: Should pass
        response = await self.client.delete(f"/users/{self.admin.id}")
        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)
        self.assertIsNone(await User.get(User.id == self.admin.id))
