from datetime import date
from http import HTTPStatus

from apps.authorization.models import Group, Permission
from apps.user.models import User
from apps.user.utils.types import UserRole
from core.unittest.async_case import AsyncTestCase


class TestUserCRUD(AsyncTestCase):
    fixtures = [
        "users",
    ]

    async def async_set_up(self):
        await super().async_set_up()
        await Group.generate_crud_objects(User.table_name())
        self.user = await User.get(username="test")
        self.admin = await User.get(role=UserRole.admin)

    async def test_get_users(self, app):
        response = await self.client.get(app.url_path_for("user-list"))
        assert HTTPStatus.OK == response.status_code
        users = response.json()
        assert len(users) >= 1

    async def test_get_user(self, app):
        expected_user = await User.get(id=1)
        response = await self.client.get(
            app.url_path_for("user-get", pk=expected_user.id)
        )

        assert HTTPStatus.OK == response.status_code

        actual_user = response.json()
        assert expected_user.model_dump(mode="json") == actual_user

    async def test_post_user(self, app):
        data = {
            "username": "jdoe",
            "first_name": "John",
            "last_name": "DOE",
            "password": (lambda: "jdoe")(),
        }
        assert await User.get(username=data["username"]) is None

        response = await self.client.post(app.url_path_for("user-create"), json=data)
        assert HTTPStatus.CREATED == response.status_code

        actual_user = response.json()
        created_user = await User.get(username=data["username"])
        assert created_user is not None
        assert created_user.username == actual_user["username"]
        assert created_user.first_name == actual_user["first_name"]
        assert created_user.last_name == actual_user["last_name"]
        assert created_user.check_password(data["password"])

    async def test_patch_user(self, app):
        user = await User(
            username="user_patch",
            first_name="Test",
            last_name="Pytest",
            password=(lambda: "test123")(),
            email="patch.user@example.test",
        ).save()
        data = {
            "username": "doej",
            "email": "john.doe@example.com",
        }

        response = await self.client.patch(
            app.url_path_for("user-patch", pk=user.id), json=data
        )
        assert HTTPStatus.UNAUTHORIZED == response.status_code

        await self.client.login(user.username)
        response = await self.client.patch(
            app.url_path_for("user-patch", pk=user.id), json=data
        )
        assert HTTPStatus.FORBIDDEN == response.status_code

        perm_table = User.table_name()
        perm_name = Permission.format_permission_name("update", User.table_name())
        update_perm = Permission(name=perm_name, target_table=perm_table)
        await user.add_permission(update_perm)

        response = await self.client.patch(
            app.url_path_for("user-patch", pk=user.id), json=data
        )
        assert HTTPStatus.OK == response.status_code

        patched_user = response.json()
        assert data["username"] == patched_user["username"]
        assert data["email"] == patched_user["email"]

    async def test_patch_user_not_found(self, app):
        data = {
            "username": "doej",
            "first_name": "Jane",
            "last_name": "DOE",
        }
        await self.client.force_login(self.admin)
        response = await self.client.patch(
            app.url_path_for("user-patch", pk=-1), json=data
        )
        assert HTTPStatus.NOT_FOUND == response.status_code

        expected_response = {
            "detail": "User not found.",
        }
        assert expected_response == response.json()

    async def test_patch_entire_user_should_not_be_possible(self, app):
        user = await User(
            username="patch_entire",
            first_name="test",
            last_name="Pytest",
            password=(lambda: "test123")(),
            email="patch.entire@example.test",
        ).save()
        data = {
            "username": "doej",
            "first_name": "Jane",
            "last_name": "DOE",
            "password": (lambda: "doej")(),
            "age": date.today().year - 1970,
            "email": "john.doe@example.com",
            "address": "115 Place de Belledonne, Chamrousse",
            "role": "active",
        }
        await self.client.login(user.username)
        perm_table = User.table_name()
        perm_name = Permission.format_permission_name("update", perm_table)
        delete_perm = Permission(name=perm_name, target_table=perm_table)
        await user.add_permission(delete_perm)
        response = await self.client.patch(
            app.url_path_for("user-update", pk=user.id), json=data
        )
        assert HTTPStatus.BAD_REQUEST == response.status_code

        expected_response = {
            "detail": "Cannot use PATCH to update entire object, use PUT instead."
        }
        assert expected_response == response.json()

    async def test_put_user(self, app):
        user = await User(
            username="user_put",
            first_name="John",
            last_name="DOE",
            password=(lambda: "jdoe")(),
            email="put.user@example.test",
        ).save()
        data = {
            "username": "put_user",
            "first_name": "Jane",
            "last_name": "DOE",
            "email": "user.put@example.com",
            "password": (lambda: "jdoe")(),
        }
        response = await self.client.put(
            app.url_path_for("user-update", pk=user.id), json=data
        )
        assert HTTPStatus.UNAUTHORIZED == response.status_code

        await self.client.user_login(user)
        response = await self.client.put(
            app.url_path_for("user-update", pk=user.id), json=data
        )
        assert HTTPStatus.FORBIDDEN == response.status_code

        perm_table = User.table_name()
        perm_name = Permission.format_permission_name("update", perm_table)
        delete_perm = Permission(name=perm_name, target_table=perm_table)
        await user.add_permission(delete_perm)
        response = await self.client.put(
            app.url_path_for("user-update", pk=user.id), json=data
        )
        assert HTTPStatus.OK == response.status_code

        user = await User.get(id=user.id)
        assert data["username"] == user.username
        assert data["email"] == user.email
        assert user.check_password(data["password"])

    async def test_put_user_not_found(self, app):
        data = {
            "username": "put_user",
            "first_name": "Jane",
            "last_name": "DOE",
            "email": "user.put@example.com",
            "password": (lambda: "jdoe")(),
        }
        await self.client.force_login(self.admin)
        response = await self.client.put(
            app.url_path_for("user-update", pk=-1), json=data
        )
        assert HTTPStatus.NOT_FOUND == response.status_code
        assert response.json() == {"detail": "User not found."}

    async def test_delete_user(self, app):
        response = await self.client.delete(
            app.url_path_for("user-delete", pk=self.user.id)
        )
        assert HTTPStatus.UNAUTHORIZED == response.status_code

        await self.client.login(self.user.username)
        response = await self.client.delete(
            app.url_path_for("user-delete", pk=self.user.id)
        )
        assert HTTPStatus.FORBIDDEN == response.status_code

        perm_table = User.table_name()
        perm_name = Permission.format_permission_name("delete", perm_table)
        delete_perm = Permission(name=perm_name, target_table=perm_table)
        await self.user.add_permission(delete_perm)
        response = await self.client.delete(
            app.url_path_for("user-delete", pk=self.user.id)
        )
        assert HTTPStatus.NO_CONTENT == response.status_code
        assert await User.get(id=self.user.id) is None

    async def test_delete_user_not_found(self, app):
        await self.client.force_login(self.admin)
        response = await self.client.delete(app.url_path_for("user-delete", pk=-1))
        assert HTTPStatus.NOT_FOUND == response.status_code
        assert response.json() == {"detail": "User not found."}

    async def test_use_token_of_deleted_user(self, app):
        user = await User(
            username="deleted_token",
            first_name="Test",
            last_name="Pytest",
            password=(lambda: "test123")(),
        ).save()
        perm_name = Permission.format_permission_name("delete", User.table_name())
        delete_perm = await Permission(
            name=perm_name, target_table=User.table_name()
        ).save()
        await user.add_permission(delete_perm)
        await self.client.user_login(user)
        await user.delete()

        response = await self.client.delete(app.url_path_for("user-delete", pk=user.id))
        assert HTTPStatus.UNAUTHORIZED == response.status_code
        assert (
            "Invalid authentication token. user does not exist."
            == response.json()["detail"]
        )
