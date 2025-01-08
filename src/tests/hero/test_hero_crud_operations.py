from http import HTTPStatus

from httpx import ASGITransport, AsyncClient

from apps.hero import Hero
from apps.hero.faker import fake_heroes
from main import app
from tests.base import AsyncTestCase

BASE_URL = "http://test"


class TestHeroCRUD(AsyncTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.client = AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL)

    async def asyncTearDown(self):
        await super().asyncTearDown()
        await self.client.aclose()

    async def test_get_heroes(self):
        response = await self.client.get("/heroes/")
        assert HTTPStatus.OK == response.status_code
        data = response.json()
        assert len(data) == 0

        await fake_heroes(self.db_service)
        response = await self.client.get("/heroes/")
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertGreaterEqual(len(response.json()), 1)

    async def test_get_hero(self):
        await fake_heroes(self.db_service)
        response = await self.client.get("/heroes/1")
        self.assertEqual(HTTPStatus.OK, response.status_code)
        hero = response.json()
        self.assertIsInstance(hero, dict)
        self.assertIn("id", hero)
        self.assertIn("name", hero)
        self.assertIn("secret_name", hero)
        self.assertIn("age", hero)

    async def test_create_heroes(self):
        hero = Hero(name="Super Test Man", secret_name="Pytest", age=1970)
        response = await self.client.post("/heroes/", data=hero)
        self.assertEqual(HTTPStatus.CREATED, response.status_code)

        hero = await self.db_service.get(Hero, Hero.id == hero.id)
        self.assertIsNotNone(hero.id)

    async def test_put_hero(self):
        hero = Hero(name="Super Test Man", secret_name="Pytest", age=1970)
        await self.db_service.insert(hero)
        data = {"name": "Test man", "secret_name": "Pytest Asyncio", "age": 1977}
        response = await self.client.put("/heroes/", data=data)
        self.assertEqual(HTTPStatus.OK, response.status_code)

        new_hero = await self.db_service.get(Hero, Hero.id == hero.id)
        self.assertEqual(data["name"], new_hero.name)
        self.assertEqual(data["secret_name"], new_hero.secret_name)
        self.assertEqual(data["age"], new_hero.age)

    async def test_put_partial_hero_should_not_be_possible(self):
        hero = Hero(name="Super Test Man", secret_name="Pytest", age=1970)
        await self.db_service.insert(hero)
        data = {"name": "Test man"}
        response = await self.client.put("/heroes/", data=data)
        self.assertEqual(HTTPStatus.METHOD_NOT_ALLOWED, response.status_code)

    async def test_patch_hero(self):
        hero = Hero(name="Super Test Man", secret_name="Pytest", age=1970)
        await self.db_service.insert(hero)
        data = {"name": "Test man"}
        response = await self.client.patch("/heroes/", data=data)
        self.assertEqual(HTTPStatus.OK, response.status_code)

        new_hero = await self.db_service.get(Hero, Hero.id == hero.id)
        self.assertEqual(data["name"], new_hero.name)

    async def test_patch_entire_hero_should_not_be_possible(self):
        hero = Hero(name="Super Test Man", secret_name="Pytest", age=1970)
        await self.db_service.insert(hero)
        data = {
            "name": "Test man",
            "secret_name": "Pytest Asyncio",
            "age": 1977,
        }
        response = await self.client.patch("/heroes/", data=data)
        self.assertEqual(HTTPStatus.METHOD_NOT_ALLOWED, response.status_code)

    async def test_delete_hero(self):
        hero = Hero(name="Super Test Man", secret_name="Pytest", age=1970)
        await self.db_service.insert(hero)
        self.assertIsNotNone(hero.id)

        response = await self.client.delete("/heroes/", params={"id": hero.id})
        self.assertEqual(HTTPStatus.NO_CONTENT, response.status_code)

        hero = await self.db_service.get(Hero, Hero.id == hero.id)
        self.assertIsNone(hero)
