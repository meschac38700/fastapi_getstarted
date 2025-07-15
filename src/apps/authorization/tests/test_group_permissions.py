import asyncio
from http import HTTPStatus

from apps.authorization.models import Group, Permission
from apps.hero.models import Hero
from apps.user.models import User
from apps.user.utils.types import UserRole
from core.unittest.async_case import AsyncTestCase


class TestGroupPermissions(AsyncTestCase):
    fixtures = [
        "users",
        "heroes",
    ]

    async def asyncSetUp(self):
        await super().asyncSetUp()
        await asyncio.gather(
            Permission.generate_crud_objects(Hero.table_name()),
            Permission.generate_crud_objects(User.table_name()),
            Group.generate_crud_objects(Hero.table_name()),
        )
        self.admin, self.user, self.active = await asyncio.gather(
            User.get(role=UserRole.admin),
            User.get(role=UserRole.staff),
            User.get(role=UserRole.active),
        )

    async def test_group_has_no_right_permissions_cannot_edit(self):
        read_permission_name = Permission.format_permission_name(
            "read", Hero.table_name()
        )
        read_group = await Group.get(name=read_permission_name)
        await self.add_permissions(read_group, [read_permission_name])
        await read_group.add_user(self.user)

        await self.client.user_login(self.user)

        data = {"secret_name": "Test edit"}
        response = await self.client.patch("/heroes/1/", json=data)
        assert HTTPStatus.FORBIDDEN == response.status_code
        assert (
            response.json()["detail"]
            == "You do not have sufficient rights to this resource."
        )

    async def test_group_permission_to_edit_resource(self):
        update_permission_name = Permission.format_permission_name(
            "update", Hero.table_name()
        )
        edit_group = await Group.get(name=update_permission_name)
        await self.add_permissions(edit_group, [update_permission_name])
        await edit_group.add_user(self.user)

        await self.client.user_login(self.user)

        hero_id = 1
        data = {"secret_name": "Test edit"}
        response = await self.client.patch(f"/heroes/{hero_id}/", json=data)
        assert HTTPStatus.OK == response.status_code

        actual_data = response.json()
        hero = await Hero.get(id=hero_id)
        assert hero_id == hero.id
        assert data["secret_name"] == hero.secret_name
        assert actual_data["secret_name"] == data["secret_name"]
        assert actual_data["id"] == hero_id

    async def test_add_permission_to_a_certain_group(self):
        group = await Group(
            name="can_do_everything_with_user_table",
            target_table=User.table_name(),
            display_name="Can do anything about user",
            description="Can do everything about user operations except those that require an administrator role.",
        ).save()
        assert group.get_permissions() == []

        perms = await Permission.filter(target_table=User.table_name())
        data = {"permissions": [perm.name for perm in perms]}
        response = await self.client.patch(
            f"/authorizations/groups/{group.id}/permissions/add/", json=data
        )
        assert HTTPStatus.UNAUTHORIZED == response.status_code

        await self.client.user_login(self.user)
        response = await self.client.patch(
            f"/authorizations/groups/{group.id}/permissions/add/", json=data
        )
        assert HTTPStatus.FORBIDDEN == response.status_code

        await self.client.user_login(self.admin)
        response = await self.client.patch(
            f"/authorizations/groups/{group.id}/permissions/add/", json=data
        )
        assert HTTPStatus.OK == response.status_code

        expected_response = [perm.model_dump(mode="json") for perm in perms]
        group = await group.refresh()
        assert group.has_permissions(perms)
        assert response.json() == expected_response

    async def test_remove_permission_to_a_certain_group(self):
        group = await Group(
            name="user_read_only",
            target_table=User.table_name(),
            display_name="Read only user informations",
        ).save()
        perms = await Permission.filter(target_table=User.table_name())
        await group.extend_permissions(perms)
        actual_ids = [perm.id for perm in group.get_permissions()]
        assert all(perm.id in actual_ids for perm in perms)

        read_permission = Permission.format_permission_name("read", User.table_name())
        data = {
            "permissions": [perm.name for perm in perms if perm.name != read_permission]
        }

        response = await self.client.patch(
            f"/authorizations/groups/{group.id}/permissions/remove/", json=data
        )
        assert HTTPStatus.UNAUTHORIZED == response.status_code

        await self.client.user_login(self.active)
        response = await self.client.patch(
            f"/authorizations/groups/{group.id}/permissions/remove/", json=data
        )
        assert HTTPStatus.FORBIDDEN == response.status_code

        await self.client.user_login(self.admin)
        response = await self.client.patch(
            f"/authorizations/groups/{group.id}/permissions/remove/", json=data
        )
        assert HTTPStatus.OK == response.status_code

        read_permission_name = Permission.format_permission_name(
            "read", User.table_name()
        )
        read_perm = await Permission.get(name=read_permission_name)
        expected_response = [read_perm.model_dump(mode="json")]
        assert response.json() == expected_response
        group = await group.refresh()
        assert group.get_permissions() == [read_perm]
