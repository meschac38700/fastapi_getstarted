from http import HTTPStatus

from httpx import ASGITransport, AsyncClient

from apps.hero.faker import fake_heroes
from main import app
from services.db import DBService
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

        async with DBService() as db:
            await fake_heroes(db)
        response = await self.client.get("/heroes/")
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertGreaterEqual(len(response.json()), 1)
