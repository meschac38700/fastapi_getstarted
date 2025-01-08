from http import HTTPStatus

from httpx import ASGITransport, AsyncClient

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
