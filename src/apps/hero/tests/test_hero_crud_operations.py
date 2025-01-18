from http import HTTPStatus
from typing import Any

from apps.hero.models import Hero
from core.test.async_case import AsyncTestCase


class TestHeroCRUD(AsyncTestCase):
    fixtures = [
        "initial-heroes",
    ]

    async def test_get_heroes(self):
        response = await self.client.get("/heroes/")
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertGreaterEqual(len(response.json()), 1)

    async def test_get_hero(self):
        response = await self.client.get("/heroes/1")
        self.assertEqual(HTTPStatus.OK, response.status_code)
        hero = response.json()
        self.assertIsInstance(hero, dict)
        self.assertIn("id", hero)
        self.assertIn("name", hero)
        self.assertIn("secret_name", hero)
        self.assertIn("age", hero)

    async def test_create_hero(self):
        hero = Hero(name="Super Test Man", secret_name="Pytest", age=1970)
        response = await self.client.post("/heroes/", json=hero.model_dump())

        self.assertEqual(HTTPStatus.CREATED, response.status_code)

        stored_hero = await Hero.get(Hero.name == "Super Test Man")
        self.assertIsInstance(stored_hero, Hero)
        hero_created: dict[str, Any] = response.json()
        self.assertIsNotNone(hero_created["id"])
        self.assertEqual(hero.name, hero_created["name"])
        self.assertEqual(hero.secret_name, hero_created["secret_name"])
        self.assertEqual(hero.age, hero_created["age"])

    async def test_put_hero(self):
        hero = await Hero(name="Super Test Man", secret_name="Pytest", age=1970).save()
        data = {"name": "Test man", "secret_name": "Pytest Asyncio", "age": 1977}
        response = await self.client.put(f"/heroes/{hero.id}", json=data)
        self.assertEqual(HTTPStatus.OK, response.status_code)

        new_hero = await self.db_service.get(Hero, Hero.id == hero.id)
        self.assertEqual(data["name"], new_hero.name)
        self.assertEqual(data["secret_name"], new_hero.secret_name)
        self.assertEqual(data["age"], new_hero.age)

    async def test_patch_hero(self):
        hero = await Hero(name="Super Test Man", secret_name="Pytest", age=1970).save()
        data = {"name": "Test man"}
        response = await self.client.patch(f"/heroes/{hero.id}", json=data)
        self.assertEqual(HTTPStatus.OK, response.status_code)

        new_hero = await self.db_service.get(Hero, Hero.id == hero.id)
        self.assertEqual(data["name"], new_hero.name)

    async def test_patch_entire_hero_should_not_be_possible(self):
        hero = await Hero(name="Super Test Man", secret_name="Pytest", age=1970).save()
        data = {
            "name": "Test man",
            "secret_name": "Pytest Asyncio",
            "age": 1977,
        }
        response = await self.client.patch(f"/heroes/{hero.id}", json=data)
        self.assertEqual(HTTPStatus.BAD_REQUEST, response.status_code)
        expected_json = {
            "detail": "Cannot use PATCH to update entire registry, use PUT instead."
        }
        self.assertEqual(expected_json, response.json())

    async def test_delete_hero(self):
        hero = await Hero(name="Super Test Man", secret_name="Pytest", age=1970).save()
        self.assertIsNotNone(hero.id)

        response = await self.client.delete(
            f"/heroes/{hero.id}", params={"id": hero.id}
        )
        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)

        hero = await self.db_service.get(Hero, Hero.id == hero.id)
        self.assertIsNone(hero)
