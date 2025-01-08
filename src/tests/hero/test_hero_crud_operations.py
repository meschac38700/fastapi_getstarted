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

    async def test_create_heroes(self):
        hero = Hero(name="Super Test Man", secret_name="Pytest", age=1970)
        response = await self.client.post("/heroes/", data=hero)
        self.assertEqual(HTTPStatus.CREATED, response.status_code)

        hero = await self.db_service.refresh(hero)
        self.assertIsNotNone(hero.id)
