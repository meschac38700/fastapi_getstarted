from http import HTTPStatus

from core.unittest.async_case import AsyncTestCase
from settings import settings


class TestDefaultRouter(AsyncTestCase):
    async def test_get_secret(self):
        response = await self.client.get("/")
        assert HTTPStatus.OK == response.status_code
        data = response.json()
        assert "secret" in data
        assert len(data["secret"]) > 65

    async def test_get_secret_with_length(self):
        length = 55
        response = await self.client.get("/", params={"length": length})
        assert len(response.json()["secret"]) > length

    async def test_heath_check(self):
        response = await self.client.get(settings.health_check_endpoint)
        expected_response = {"status": "ok"}

        assert response.status_code == HTTPStatus.OK
        assert expected_response == response.json()
