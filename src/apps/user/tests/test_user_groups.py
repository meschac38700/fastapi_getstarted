import asyncio
from http import HTTPStatus

from apps.authorization.models import Group, Permission
from apps.user.models import User
from apps.user.utils.types import UserRole
from core.unittest.async_case import AsyncTestCase


class TestUserGroup(AsyncTestCase):
    fixtures = ["users"]

    async def async_set_up(self):
        await super().async_set_up()
        await Group.generate_crud_objects(User.table_name())
        self.active, self.staff, self.admin = await asyncio.gather(
            User.get(role=UserRole.active),
            User.get(role=UserRole.staff),
            User.get(role=UserRole.admin),
        )

    async def test_get_own_groups_using_admin_endpoint_denied(self):
        response = await self.client.get(f"/users/{self.staff.id}/groups/")
        assert HTTPStatus.UNAUTHORIZED == response.status_code

        await self.client.user_login(self.staff)

        # endpoint reserved to admin user
        response = await self.client.get(f"/users/{self.staff.id}/groups/")
        assert HTTPStatus.FORBIDDEN == response.status_code
        assert (
            "Insufficient rights to carry out this action" == response.json()["detail"]
        )

    async def test_get_own_user_groups(self):
        response = await self.client.get("/users/groups/")
        assert HTTPStatus.UNAUTHORIZED == response.status_code

        await self.client.user_login(self.staff)

        expected_groups = [
            Permission.format_permission_name("read", User.table_name()),
            Permission.format_permission_name("create", User.table_name()),
            Permission.format_permission_name("update", User.table_name()),
        ]
        await self.staff.add_to_groups(await Group.filter(name__in=expected_groups))

        response = await self.client.get("/users/groups/")
        assert HTTPStatus.OK == response.status_code

        assert len(response.json()) >= len(expected_groups)
        assert all(perm["name"] in expected_groups for perm in response.json())

    async def test_admin_get_user_groups(self):
        response = await self.client.get(f"/users/{self.active.id}/groups/")
        assert HTTPStatus.UNAUTHORIZED == response.status_code

        await self.client.user_login(self.admin)

        # Get groups of active user
        expected_groups = [
            Permission.format_permission_name("read", User.table_name()),
            Permission.format_permission_name("create", User.table_name()),
            Permission.format_permission_name("update", User.table_name()),
        ]
        await self.active.add_to_groups(await Group.filter(name__in=expected_groups))

        response = await self.client.get(f"/users/{self.active.id}/groups/")
        assert HTTPStatus.OK == response.status_code
        assert len(response.json()) >= len(expected_groups)
        assert all(group["name"] in expected_groups for group in response.json())

        # Get groups of staff user
        await self.staff.add_to_groups(await Group.filter(name__in=expected_groups))
        response = await self.client.get(f"/users/{self.staff.id}/groups/")
        assert HTTPStatus.OK == response.status_code

        assert len(response.json()) >= len(expected_groups)
        assert all(group["name"] in expected_groups for group in response.json())
