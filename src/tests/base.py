from unittest.async_case import IsolatedAsyncioTestCase

from httpx import ASGITransport, AsyncClient

from core.db import create_db_and_tables, delete_db_and_tables
from main import app
from settings import settings

BASE_URL = "http://test"
_engine = settings.get_engine()


class AsyncTestCase(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        await create_db_and_tables(_engine)
        self.client = AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL)

    async def asyncTearDown(self):
        await super().asyncTearDown()
        await delete_db_and_tables(_engine)
        await self.client.aclose()
