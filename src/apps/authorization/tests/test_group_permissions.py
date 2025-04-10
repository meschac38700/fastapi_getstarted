import asyncio
from http import HTTPStatus

from apps.authorization.models import Group, Permission
from apps.hero.models import Hero
from apps.user.models import User
from apps.user.utils.types import UserRole
from core.testing.async_case import AsyncTestCase


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
        read_group = await Group.get(name="read_hero")
        await self.add_permissions(read_group, ["read_hero"])
        await read_group.add_user(self.user)

        await self.client.user_login(self.user)

        data = {"secret_name": "Test edit"}
        response = await self.client.patch("/heroes/1/", json=data)
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)
        self.assertEqual(
            response.json()["detail"],
            "You do not have sufficient rights to this resource.",
        )

    async def test_group_permission_to_edit_resource(self):
        edit_group = await Group.get(name="update_hero")
        await self.add_permissions(edit_group, ["update_hero"])
        await edit_group.add_user(self.user)

        await self.client.user_login(self.user)

        hero_id = 1
        data = {"secret_name": "Test edit"}
        response = await self.client.patch(f"/heroes/{hero_id}/", json=data)
        self.assertEqual(HTTPStatus.OK, response.status_code)

        actual_data = response.json()
        hero = await Hero.get(id=hero_id)
        self.assertEqual(hero_id, hero.id)
        self.assertEqual(data["secret_name"], hero.secret_name)
        self.assertEqual(actual_data["secret_name"], data["secret_name"])
        self.assertEqual(actual_data["id"], hero_id)

    async def test_add_permission_to_a_certain_group(self):
        group = await Group(
            name="can_do_everything_with_user_table",
            target_table=User.table_name(),
            display_name="Can do anything about user",
            description="Can do everything about user operations except those that require an administrator role.",
        ).save()
        self.assertEqual(group.get_permissions(), [])

        perms = await Permission.filter(target_table=User.table_name())
        data = {"permissions": [perm.name for perm in perms]}
        response = await self.client.post(
            f"/authorizations/groups/{group.id}/permissions/add/", json=data
        )
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)

        await self.client.user_login(self.user)
        response = await self.client.post(
            f"/authorizations/groups/{group.id}/permissions/add/", json=data
        )
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)

        await self.client.user_login(self.admin)
        response = await self.client.post(
            f"/authorizations/groups/{group.id}/permissions/add/", json=data
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)

        expected_response = [perm.model_dump(mode="json") for perm in perms]
        group = await group.refresh()
        self.assertTrue(group.has_permissions(perms))
        self.assertEqual(response.json(), expected_response)

    async def test_remove_permission_to_a_certain_group(self):
        group = await Group(
            name="user_read_only",
            target_table=User.table_name(),
            display_name="Read only user informations",
        ).save()
        perms = await Permission.filter(target_table=User.table_name())
        await group.extend_permissions(perms)
        self.assertEqual(group.get_permissions(), perms)

        data = {
            "permissions": [perm.name for perm in perms if perm.name != "read_users"]
        }

        response = await self.client.post(
            f"/authorizations/groups/{group.id}/permissions/remove/", json=data
        )
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)

        await self.client.user_login(self.active)
        response = await self.client.post(
            f"/authorizations/groups/{group.id}/permissions/remove/", json=data
        )
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)

        await self.client.user_login(self.admin)
        response = await self.client.post(
            f"/authorizations/groups/{group.id}/permissions/remove/", json=data
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)

        read_perm = await Permission.get(name="read_users")
        expected_response = [read_perm.model_dump(mode="json")]
        self.assertEqual(response.json(), expected_response)
        group = await group.refresh()
        self.assertEqual(group.get_permissions(), [read_perm])
