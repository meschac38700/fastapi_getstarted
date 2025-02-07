import asyncio
from datetime import date
from http import HTTPStatus

from apps.authorization.models.group import Group
from apps.authorization.models.permission import Permission
from apps.user.models import User
from core.test.async_case import AsyncTestCase


class TestUserCRUD(AsyncTestCase):
    fixtures = [
        "users",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        asyncio.run(Permission.generate_crud_objects(User.table_name()))
        asyncio.run(Group.generate_crud_objects(User.table_name()))
        cls.user = asyncio.run(User.get(User.username == "test"))

    async def test_get_users(self):
        response = await self.client.get("/users/")
        self.assertEqual(HTTPStatus.OK, response.status_code)
        users = response.json()
        self.assertGreaterEqual(len(users), 1)

    async def test_get_user(self):
        expected_user = await User.get(User.id == 1)
        response = await self.client.get(f"/users/{expected_user.id}/")

        self.assertEqual(HTTPStatus.OK, response.status_code)

        actual_user = response.json()
        self.assertDictEqual(expected_user.model_dump(mode="json"), actual_user)

    async def test_post_user(self):
        data = {
            "username": "jdoe",
            "first_name": "John",
            "last_name": "DOE",
            "password": "jdoe",
        }
        self.assertIsNone(await User.get(User.username == data["username"]))

        response = await self.client.post("/users/", json=data)
        self.assertEqual(HTTPStatus.CREATED, response.status_code)

        actual_user = response.json()
        created_user = await User.get(User.username == data["username"])
        self.assertIsNotNone(created_user)
        self.assertEqual(created_user.username, actual_user["username"])
        self.assertEqual(created_user.first_name, actual_user["first_name"])
        self.assertEqual(created_user.last_name, actual_user["last_name"])
        self.assertTrue(created_user.check_password(data["password"]))

    async def test_patch_user(self):
        user = await User(
            username="user_patch",
            first_name="Test",
            last_name="Pytest",
            password="test123",
            email="patch.user@example.test",
        ).save()
        data = {
            "username": "doej",
            "email": "john.doe@example.com",
        }

        response = await self.client.patch(f"/users/{user.id}/", json=data)
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)

        await self.client.login(user.username)
        response = await self.client.patch(f"/users/{user.id}/", json=data)
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)

        await self.add_permissions(user, ["update_user"])
        response = await self.client.patch(f"/users/{user.id}/", json=data)
        self.assertEqual(HTTPStatus.OK, response.status_code)

        patched_user = response.json()
        self.assertEqual(data["username"], patched_user["username"])
        self.assertEqual(data["email"], patched_user["email"])

    async def test_patch_entire_user_should_not_be_possible(self):
        user = await User(
            username="patch_entire",
            first_name="test",
            last_name="Pytest",
            password="test123",
            email="patch.entire@example.test",
        ).save()
        data = {
            "username": "doej",
            "first_name": "Jane",
            "last_name": "DOE",
            "password": "doej",
            "age": date.today().year - 1970,
            "email": "john.doe@example.com",
            "address": "115 Place de Belledonne, Chamrousse",
        }
        response = await self.client.patch(f"/users/{user.id}/", json=data)
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)

        await self.client.login(user.username)
        response = await self.client.patch(f"/users/{user.id}/", json=data)
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)

        await self.add_permissions(user, ["update_user"])
        response = await self.client.patch(f"/users/{user.id}/", json=data)
        self.assertEqual(HTTPStatus.BAD_REQUEST, response.status_code)

        expected_response = {
            "detail": "Cannot use PATCH to update entire object, use PUT instead."
        }
        self.assertEqual(expected_response, response.json())

    async def test_put_user(self):
        user = await User(
            username="user_put",
            first_name="John",
            last_name="DOE",
            password="jdoe",
            email="put.user@example.test",
        ).save()
        data = {
            "username": "put_user",
            "first_name": "Jane",
            "last_name": "DOE",
            "email": "user.put@example.com",
            "password": "jdoe",
        }
        response = await self.client.put(f"/users/{user.id}/", json=data)
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)

        await self.client.user_login(user)
        response = await self.client.put(f"/users/{user.id}/", json=data)
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)

        await self.add_permissions(user, ["update_user"])
        response = await self.client.put(f"/users/{user.id}/", json=data)
        self.assertEqual(HTTPStatus.OK, response.status_code)

        user = await User.get(User.id == user.id)
        self.assertEqual(data["username"], user.username)
        self.assertEqual(data["email"], user.email)
        self.assertTrue(user.check_password(data["password"]))

    async def test_delete_user(self):
        response = await self.client.delete(f"/users/{self.user.id}/")
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)

        await self.client.login(self.user.username)
        response = await self.client.delete(f"/users/{self.user.id}/")
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)

        await self.add_permissions(self.user, ["delete_user"])
        response = await self.client.delete(f"/users/{self.user.id}/")
        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)
        self.assertIsNone(await User.get(User.id == self.user.id))

    async def test_use_token_of_deleted_user(self):
        user = await User(
            username="deleted_token",
            first_name="Test",
            last_name="Pytest",
            password="test123",
        ).save()
        await self.add_permissions(user, ["delete_user"])
        await self.client.user_login(user)
        await user.delete()

        response = await self.client.delete(f"/users/{user.id}/")
        self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)
        self.assertEqual(
            "Invalid authentication token. user does not exist.",
            response.json()["detail"],
        )
