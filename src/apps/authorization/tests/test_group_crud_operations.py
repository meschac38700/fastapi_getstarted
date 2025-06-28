import asyncio
from http import HTTPStatus

from apps.authorization.models import Group, Permission
from apps.user.models import User
from apps.user.utils.types import UserRole
from core.unittest.async_case import AsyncTestCase


class TestGroupCRUD(AsyncTestCase):
    fixtures = [
        "users",
    ]

    async def asyncSetUp(self):
        await super().asyncSetUp()

        await Permission.generate_crud_objects(Permission.table_name())
        await Group.generate_crud_objects(Permission.table_name())

        self.admin, self.staff = await asyncio.gather(
            User.get(role=UserRole.admin), User.get(role=UserRole.staff)
        )

    async def test_get_group_with_staff_user_permission_denied(self):
        await self.client.user_login(self.staff)

        response = await self.client.get("authorizations/groups/")
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)
        self.assertEqual(
            "Insufficient rights to carry out this action",
            response.json()["detail"],
        )

    async def test_get_group_with_admin_user(self):
        await self.client.user_login(self.admin)

        response = await self.client.get("authorizations/groups/")
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertGreaterEqual(len(response.json()), 4)

    async def test_get_group_filter_by_name(self):
        await self.client.user_login(self.admin)
        read_permission_name = Permission.format_permission_name(
            "read", Permission.table_name()
        )
        response = await self.client.get(
            "authorizations/groups/", params={"name": read_permission_name}
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)
        expected = {
            "name": read_permission_name,
            "target_table": Permission.table_name(),
            "display_name": "Read permission",
            "description": "This permission_group allows user to read the Permission model.",
        }
        data = response.json()
        self.assertEqual(len(data), 1)
        actual = data[0]
        actual.pop("id", None)
        self.assertEqual(actual, expected)

    async def test_get_group_filter_by_target_table(self):
        await self.client.user_login(self.admin)

        response = await self.client.get(
            "authorizations/groups/", params={"target_table": Permission.table_name()}
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertGreaterEqual(len(response.json()), 4)

    async def test_get_group_filter_by_name_and_target_table(self):
        await self.client.user_login(self.admin)
        create_permission_name = Permission.format_permission_name(
            "create", Permission.table_name()
        )
        response = await self.client.get(
            "authorizations/groups/",
            params={
                "name": create_permission_name,
                "target_table": Permission.table_name(),
            },
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)
        expected = {
            "name": create_permission_name,
            "target_table": Permission.table_name(),
            "display_name": "Create permission",
            "description": "This permission_group allows user to create the Permission model.",
        }
        data = response.json()
        self.assertEqual(len(data), 1)
        actual = data[0]
        self.assertIsInstance(actual.pop("id", None), int)
        self.assertEqual(actual, expected)

    async def test_add_new_group(self):
        post_data = {
            "name": "list_user_permissions",
            "target_table": Permission.table_name(),
            "display_name": "List all user's permissions",
        }
        response = await self.client.post("/authorizations/groups/", json=post_data)
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)

        await self.client.user_login(self.staff)

        response = await self.client.post("/authorizations/groups/", json=post_data)
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)

        await self.client.force_login(self.admin)

        response = await self.client.post("/authorizations/groups/", json=post_data)
        self.assertEqual(HTTPStatus.CREATED, response.status_code)

        actual_data = response.json()
        created_group_id = actual_data.pop("id", None)
        self.assertIsNotNone(created_group_id)
        self.assertIsNotNone(await Group.get(id=created_group_id))
        self.assertTrue(all(actual_data[k] == v for k, v in post_data.items()))

    async def test_patch_group(self):
        update_data = {
            "description": "New group description",
            "display_name": "Delete admin account Modified",
        }
        group = await Group(
            name="patch_test_group", target_table=Permission.table_name()
        ).save()
        response = await self.client.patch(
            f"/authorizations/groups/{group.id}/", json=update_data
        )
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)

        await self.client.user_login(self.staff)

        response = await self.client.patch(
            f"/authorizations/groups/{group.id}/", json=update_data
        )
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)

        await self.client.force_login(self.admin)

        response = await self.client.patch(
            f"/authorizations/groups/{group.id}/", json=update_data
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)

        actual_data = response.json()
        self.assertIsNotNone(actual_data.pop("id", None))
        self.assertTrue(all(actual_data[k] == v for k, v in update_data.items()))

    async def test_put_group(self):
        update_data = {
            "name": "update_test_permission_modified",
            "target_table": "permission_test",
        }
        group = await Group(
            name="update_test_permission", target_table=Permission.table_name()
        ).save()
        response = await self.client.put(
            f"/authorizations/groups/{group.id}/", json=update_data
        )
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)

        await self.client.user_login(self.staff)

        response = await self.client.put(
            f"/authorizations/groups/{group.id}/", json=update_data
        )
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)

        await self.client.force_login(self.admin)

        response = await self.client.put(
            f"/authorizations/groups/{group.id}/", json=update_data
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)

        actual_data = response.json()
        self.assertIsNotNone(actual_data.pop("id", None))
        self.assertTrue(all(actual_data[k] == v for k, v in update_data.items()))

    async def test_delete_group(self):
        group = await Group(
            name="delete_test_permission", target_table=Permission.table_name()
        ).save()
        response = await self.client.delete(f"/authorizations/groups/{group.id}/")
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)

        await self.client.user_login(self.staff)

        response = await self.client.delete(f"/authorizations/groups/{group.id}/")
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)

        await self.client.force_login(self.admin)

        response = await self.client.delete(f"/authorizations/groups/{group.id}/")
        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)

        self.assertIsNone(await Group.get(id=group.id))
