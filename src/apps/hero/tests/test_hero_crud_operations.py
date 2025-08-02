from http import HTTPStatus
from typing import Any

from apps.authorization.models import Group, Permission
from apps.hero.models import Hero
from apps.user.models import User
from core.unittest.async_case import AsyncTestCase


class TestHeroCRUD(AsyncTestCase):
    fixtures = [
        "users",
        "heroes",
    ]

    async def async_set_up(self):
        await super().async_set_up()
        await Permission.generate_crud_objects(Hero.table_name())
        await Group.generate_crud_objects(Hero.table_name())
        self.user = await User.get(username="test")

    async def test_get_heroes(self, app):
        response = await self.client.get(app.url_path_for("hero-list"))
        assert HTTPStatus.OK == response.status_code
        assert len(response.json()) >= 1

    async def test_get_hero(self, app):
        response = await self.client.get(app.url_path_for("hero-get", pk=1))
        assert HTTPStatus.OK == response.status_code

        hero = response.json()
        assert isinstance(hero, dict)
        assert "id" in hero
        assert "name" in hero
        assert "secret_name" in hero
        assert "age" in hero

    async def test_create_hero(self, app):
        hero = Hero(name="Super Test Man", secret_name="Pytest", age=1970)
        response = await self.client.post(
            app.url_path_for("hero-create"), json=hero.model_dump(mode="json")
        )
        assert HTTPStatus.UNAUTHORIZED == response.status_code

        await self.client.user_login(self.user)

        response = await self.client.post(
            app.url_path_for("hero-create"), json=hero.model_dump(mode="json")
        )
        assert HTTPStatus.FORBIDDEN == response.status_code

        create_perm = Permission.format_permission_name("create", Hero.table_name())
        group_create = await Group.get(name=create_perm)
        await self.add_permissions(group_create, [create_perm])
        await group_create.add_user(self.user)

        response = await self.client.post(
            app.url_path_for("hero-create"), json=hero.model_dump(mode="json")
        )
        assert HTTPStatus.CREATED == response.status_code

        stored_hero = await Hero.get(name="Super Test Man")
        assert isinstance(stored_hero, Hero)

        hero_created: dict[str, Any] = response.json()
        assert hero_created["id"] is not None
        assert hero.name == hero_created["name"]
        assert hero.secret_name == hero_created["secret_name"]
        assert hero.age == hero_created["age"]

    async def test_put_hero(self, app):
        hero = await Hero(name="Super Test Man", secret_name="Pytest", age=1970).save()
        data = {"name": "Test man", "secret_name": "Pytest Asyncio", "age": 1977}

        response = await self.client.put(
            app.url_path_for("hero-update", pk=hero.id), json=data
        )
        assert HTTPStatus.UNAUTHORIZED == response.status_code

        user = await User(
            username="user_put",
            first_name="Test",
            last_name="Pytest",
            password=(lambda: "pytest123")(),
        ).save()

        await self.client.user_login(user)
        response = await self.client.put(
            app.url_path_for("hero-update", pk=hero.id), json=data
        )
        assert HTTPStatus.FORBIDDEN == response.status_code

        update_perm = Permission.format_permission_name("update", Hero.table_name())
        update_hero_perm = await Permission.get(name=update_perm)
        await user.add_permission(update_hero_perm)

        response = await self.client.put(
            app.url_path_for("hero-update", pk=hero.id), json=data
        )
        assert HTTPStatus.OK == response.status_code

        new_hero = await Hero.get(id=hero.id)
        assert data["name"] == new_hero.name
        assert data["secret_name"] == new_hero.secret_name
        assert data["age"] == new_hero.age

    async def test_patch_hero(self, app):
        hero = await Hero(name="Super Test Man", secret_name="Pytest", age=1970).save()
        data = {"name": "Test man"}

        response = await self.client.patch(
            app.url_path_for("hero-patch", pk=hero.id), json=data
        )
        assert HTTPStatus.UNAUTHORIZED == response.status_code

        user = await User(
            username="user_patch",
            first_name="Test",
            last_name="Pytest",
            password=(lambda: "pytest123")(),
        ).save()
        await self.client.user_login(user)
        response = await self.client.patch(
            app.url_path_for("hero-patch", pk=hero.id), json=data
        )
        assert HTTPStatus.FORBIDDEN == response.status_code

        update_perm = Permission.format_permission_name("update", Hero.table_name())
        update_hero_perm = await Permission.get(name=update_perm)
        await user.add_permission(update_hero_perm)

        response = await self.client.patch(
            app.url_path_for("hero-patch", pk=hero.id), json=data
        )
        assert HTTPStatus.OK == response.status_code

        new_hero = await Hero.get(id=hero.id)
        assert data["name"] == new_hero.name

    async def test_patch_entire_hero_should_not_be_possible(self, app):
        hero = await Hero(name="Super Test Man", secret_name="Pytest", age=1970).save()
        data = {
            "name": "Test man",
            "secret_name": "Pytest Asyncio",
            "age": 1977,
            "user_id": 1,
        }

        await self.client.user_login(self.user)

        update_perm = Permission.format_permission_name("update", Hero.table_name())
        group_create = await Group.get(name=update_perm)
        await self.add_permissions(group_create, [update_perm])
        await group_create.add_user(self.user)

        response = await self.client.patch(
            app.url_path_for("hero-patch", pk=hero.id), json=data
        )
        assert HTTPStatus.BAD_REQUEST == response.status_code

        expected_json = {
            "detail": "Cannot use PATCH to update entire registry, use PUT instead."
        }
        assert expected_json == response.json()

    async def test_delete_hero(self, app):
        hero = await Hero(name="Super Test Man", secret_name="Pytest", age=1970).save()
        assert hero.id is not None

        response = await self.client.delete(
            app.url_path_for("hero-delete", pk=hero.id), params={"id": hero.id}
        )
        assert HTTPStatus.UNAUTHORIZED == response.status_code

        await self.client.user_login(self.user)
        response = await self.client.delete(
            app.url_path_for("hero-delete", pk=hero.id), params={"id": hero.id}
        )
        assert HTTPStatus.FORBIDDEN == response.status_code

        delete_perm = Permission.format_permission_name("delete", Hero.table_name())
        group_create = await Group.get(name=delete_perm)
        await self.add_permissions(group_create, [delete_perm])
        await group_create.add_user(self.user)

        response = await self.client.delete(
            app.url_path_for("hero-delete", pk=hero.id), params={"id": hero.id}
        )
        assert HTTPStatus.NO_CONTENT == response.status_code

        hero = await self.db_service.get(Hero, id=hero.id)
        assert hero is None
