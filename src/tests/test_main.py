from http import HTTPStatus

import pytest
from httpx import ASGITransport, AsyncClient

from main import app

BASE_URL = "https://test"


@pytest.mark.anyio
async def test_get_secret():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=BASE_URL
    ) as client:
        response = await client.get("/")
        assert HTTPStatus.OK == response.status_code
        data = response.json()
        assert "secret" in data
        assert len(data["secret"]) > 65


@pytest.mark.anyio
async def test_get_secret_with_length():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=BASE_URL
    ) as client:
        length = 55
        response = await client.get("/", params={"length": length})
        assert len(response.json()["secret"]) > length
