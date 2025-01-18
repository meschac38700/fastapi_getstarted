from datetime import date
from http import HTTPStatus

from apps.user.models import User
from core.test.async_case import AsyncTestCase


class TestUserCRUD(AsyncTestCase):
    fixtures = [
        "test-users",
    ]

    async def test_get_users(self):
        response = await self.client.get("/users/")
        self.assertEqual(HTTPStatus.OK, response.status_code)
        users = response.json()
        self.assertGreaterEqual(len(users), 1)

    async def test_get_user(self):
        expected_user = await User.get(User.id == 1)
        response = await self.client.get(f"/users/{expected_user.id}")

        self.assertEqual(HTTPStatus.OK, response.status_code)
        actual_user = response.json()

        self.assertDictEqual(expected_user.model_dump(), actual_user)

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
            username="jdoe",
            first_name="John",
            last_name="DOE",
            password="jdoe",
            email="jdoe@example.test",
        ).save()
        data = {
            "username": "doej",
            "email": "john.doe@example.com",
        }
        response = await self.client.patch(f"/users/{user.id}", json=data)
        self.assertEqual(HTTPStatus.OK, response.status_code)

        patched_user = response.json()

        self.assertEqual(data["username"], patched_user["username"])
        self.assertEqual(data["email"], patched_user["email"])

    async def test_patch_entire_user_should_not_be_possible(self):
        user = await User(
            username="jdoe",
            first_name="John",
            last_name="DOE",
            password="jdoe",
            email="jdoe@example.test",
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
        response = await self.client.patch(f"/users/{user.id}", json=data)
        self.assertEqual(HTTPStatus.BAD_REQUEST, response.status_code)

        expected_response = {
            "detail": "Cannot use PATCH to update entire object, use PUT instead."
        }
        self.assertEqual(expected_response, response.json())

    async def test_put_user(self):
        user = await User(
            username="jdoe",
            first_name="John",
            last_name="DOE",
            password="jdoe",
            email="jdoe@example.test",
        ).save()
        data = {
            "username": "doej",
            "first_name": "jane",
            "last_name": "DOE",
            "email": "john.doe@example.com",
            "password": "jdoe",
        }
        response = await self.client.patch(f"/users/{user.id}", json=data)
        self.assertEqual(HTTPStatus.OK, response.status_code)

        user = await User.get(User.id == user.id)

        self.assertEqual(data["username"], user.username)
        self.assertEqual(data["email"], user.email)
        self.assertTrue(user.check_password(data["password"]))

    async def test_delete_user(self):
        user_to_delete = await User.get(User.id == 1)
        self.assertIsNotNone(user_to_delete)

        response = await self.client.delete(f"/users/{user_to_delete.id}")
        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)

        self.assertIsNone(await User.get(User.id == user_to_delete.id))
